import gspread, os
from core.database import get_connection
from core.logger import criar_logger

CAMINHO_CREDENCIAL = os.getenv(
    "CAMINHO_CREDENCIAL_CONTA_SERVICO"
)

SPREADSHEET_ID = os.getenv(
    "SPREADSHEET_ID"
)

COLUNA_CODIGO = 2

MODO_TESTE = False

logger = criar_logger(
    "atualizador",
    "atualizacoes.log"
)

def conectar_google_sheets():
    cliente = gspread.service_account(
        filename=CAMINHO_CREDENCIAL
    )

    planilha = cliente.open_by_key(SPREADSHEET_ID)

    return planilha

def extrair_codigos(planilha):

    codigos = []

    abas = planilha.worksheets()

    for aba in abas:

        print(f"Processando aba: {aba.title}")

        dados = aba.get_all_values()

        quantidade_aba = 0

        for numero_linha, linha in enumerate(dados[1:], start=2):

            if len(linha) >= COLUNA_CODIGO:

                codigo = linha[COLUNA_CODIGO - 1].strip()

                if codigo:

                    codigos.append({
                        "aba": aba.title,
                        "linha": numero_linha,
                        "codigo": codigo
                    })

                    quantidade_aba += 1

        print(
            f"  → {quantidade_aba} códigos encontrados"
        )

    return codigos

def atualizar_estoque_linha(aba, linha, dados_estoque):

    valores = [[
        dados_estoque["FOZ DO IGUACU"],
        dados_estoque["UMUARAMA"],
        dados_estoque["TOLEDO"],
        dados_estoque["CASCAVEL"],
        sum(dados_estoque.values())
    ]]

    aba.update(
        range_name=f"E{linha}:I{linha}",
        values=valores
    )

def consultar_estoque(codigos):

    if not codigos:
        return []

    conexao = get_connection('read')

    cursor = conexao.cursor()

    # Cria os parâmetros :codigo0, :codigo1, :codigo2...
    placeholders = []

    parametros = {}

    for indice, codigo in enumerate(codigos):

        nome_parametro = f"codigo{indice}"

        placeholders.append(f":{nome_parametro}")

        parametros[nome_parametro] = codigo

    lista_in = ", ".join(placeholders)

    query = f"""
        SELECT
            itm.item_estoque_pub AS codigo,
            rev.cidade,
            pec.qtd_contabil
        FROM pec_item_revenda pec

        INNER JOIN pec_item_estoque itm
            ON pec.empresa = itm.empresa
            AND pec.item_estoque = itm.item_estoque

        INNER JOIN ger_revenda rev
            ON pec.empresa = rev.empresa
            AND pec.revenda = rev.revenda

        WHERE
            pec.empresa = 1
            AND itm.item_estoque_pub IN ({lista_in})

        ORDER BY
            itm.item_estoque_pub,
            pec.revenda
    """

    cursor.execute(
        query,
        parametros
    )

    resultados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return resultados

def organizar_estoque(resultados):

    estoque = {}

    for codigo, cidade, quantidade in resultados:

        if codigo not in estoque:
            estoque[codigo] = {
                "FOZ DO IGUACU": 0,
                "UMUARAMA": 0,
                "TOLEDO": 0,
                "CASCAVEL": 0
            }

        cidade = cidade.strip().upper()

        if cidade in estoque[codigo]:
            estoque[codigo][cidade] += quantidade

    return estoque

def preparar_atualizacoes(codigos_planilha, estoque):

    atualizacoes = {}

    for item in codigos_planilha:

        aba = item["aba"]
        linha = item["linha"]
        codigo = item["codigo"]

        dados_estoque = estoque.get(
            codigo,
            {
                "FOZ DO IGUACU": 0,
                "UMUARAMA": 0,
                "TOLEDO": 0,
                "CASCAVEL": 0
            }
        )

        total = sum(dados_estoque.values())

        valores = [
            dados_estoque["FOZ DO IGUACU"],
            dados_estoque["UMUARAMA"],
            dados_estoque["TOLEDO"],
            dados_estoque["CASCAVEL"],
            total
        ]

        if aba not in atualizacoes:
            atualizacoes[aba] = []

        atualizacoes[aba].append({
            "linha": linha,
            "codigo": codigo,
            "valores": valores
        })

    return atualizacoes

def atualizar_planilha(planilha, atualizacoes):

    for nome_aba, itens in atualizacoes.items():

        aba = planilha.worksheet(nome_aba)

        print(f"\nAtualizando aba: {nome_aba}")

        operacoes = []

        for item in itens:

            linha = item["linha"]
            valores = item["valores"]

            operacoes.append({
                "range": f"E{linha}:I{linha}",
                "values": [valores]
            })

        if MODO_TESTE:

            print(
                f"  MODO TESTE: "
                f"{len(operacoes)} linhas seriam atualizadas"
            )

        else:

            aba.batch_update(operacoes)

            print(
                f"  ✓ {len(operacoes)} linhas atualizadas"
            )

def main():
    logger.info("========================================")
    logger.info("INICIANDO ATUALIZAÇÃO DE ESTOQUE")
    logger.info("========================================")

    try:
        # ==============================
            # GOOGLE SHEETS
            # ==============================
        
            planilha = conectar_google_sheets()
        
            print(f"\nPlanilha: {planilha.title}\n")
        
            codigos_planilha = extrair_codigos(planilha)

            logger.info(
            f"Registros encontrados na planilha: "
            f"{len(codigos_planilha)}"
            )

            print("\n==============================")
            print("GOOGLE SHEETS")
            print("==============================")
        
            print(
                f"Registros encontrados: "
                f"{len(codigos_planilha)}"
            )
        
        
            # ==============================
            # CÓDIGOS ÚNICOS
            # ==============================
        
            codigos_unicos = sorted(
                set(
                    item["codigo"]
                    for item in codigos_planilha
                )
            )
            logger.info(
            f"Códigos únicos: "
            f"{len(codigos_unicos)}"
            )
            print(
                f"Códigos únicos: "
                f"{len(codigos_unicos)}"
            )
        
        
            # ==============================
            # ORACLE
            # ==============================
        
            print("\nConsultando Oracle...")
        
            resultados = consultar_estoque(
                codigos_unicos
            )
        
            print(
                f"Registros retornados pelo Oracle: "
                f"{len(resultados)}"
            )
            logger.info(
            f"Registros retornados pelo Oracle: "
            f"{len(resultados)}"
            )
        
            # ==============================
            # ORGANIZAR ESTOQUE
            # ==============================
        
            estoque = organizar_estoque(
                resultados
            )
        
        
            # ==============================
            # PREPARAR ATUALIZAÇÕES
            # ==============================
        
            atualizacoes = preparar_atualizacoes(
                codigos_planilha,
                estoque
            )
        
        
            # ==============================
            # ATUALIZAR PLANILHA
            # ==============================
        
            atualizar_planilha(
                planilha,
                atualizacoes
            )
            logger.info(
            f"Linhas atualizadas: {len(atualizacoes)}"
            )
            logger.info("ATUALIZAÇÃO CONCLUÍDA")
    except Exception as e:
        print("Ocorreu um erro: ", e)
        logger.exception(
            "ERRO DURANTE A ATUALIZAÇÃO",e
        )
if __name__ == "__main__":
    main()