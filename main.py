import gspread
from core.database import get_connection

CAMINHO_CREDENCIAL = "credentials/estoque-minimo-acess-0fc284ebb331.json"

SPREADSHEET_ID = "1KTwTGhmgD5qhBZk9rKAY18ju-GiEWv2wpRN7TF2ahbU"

COLUNA_CODIGO = 2
 

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

        for linha in dados[1:]:
            if len(linha) >= COLUNA_CODIGO:
                codigo = linha[COLUNA_CODIGO - 1].strip()

                if codigo:
                    codigos.append({
                        "aba": aba.title,
                        "codigo": codigo
                    })

    return codigos

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

def main():
    
    planilha = conectar_google_sheets()
    """
    print(f"Planilha conectada: {planilha.title}\n")

    codigos = extrair_codigos(planilha)

    print(f"\nTotal de códigos encontrados: {len(codigos)}")

    for item in codigos:
        print(
            f"Aba: {item['aba']} | "
            f"Código: {item['codigo']}"
        )
    """
    codigos = extrair_codigos(planilha)
    codigos_unicos = sorted(
        set(item["codigo"] for item in codigos)
    )
    print("Consultando códigos:\n")

    resultados = consultar_estoque(codigos_unicos)

    for codigo, cidade, quantidade in resultados:

        print(
            f"{codigo} | "
            f"{cidade} | "
            f"{quantidade}"
        )


if __name__ == "__main__":
    main()