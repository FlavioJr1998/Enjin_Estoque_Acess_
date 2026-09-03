import json
import os

from datetime import datetime, timedelta

import gspread

from dotenv import load_dotenv

from core.logger import criar_logger
from core.mailer import enviar_email
from monitor import (
    verificar_estoque,
    gerar_email_alerta
)


load_dotenv()


logger = criar_logger(
    "monitoramento",
    "monitoramento.log"
)


SPREADSHEET_ID = os.getenv(
    "SPREADSHEET_ID"
)

CAMINHO_CREDENCIAL = os.getenv(
    "CAMINHO_CREDENCIAL_CONTA_SERVICO"
)

COLUNA_CODIGO = 2
COLUNA_DESCRICAO = 4
COLUNA_ESTOQUE_TOTAL = 9
COLUNA_ESTOQUE_MINIMO = 10

CAMINHO_ESTADO = (
    "data/monitoramento.json"
)


def conectar_google_sheets():

    cliente = gspread.service_account(
        filename=CAMINHO_CREDENCIAL
    )

    planilha = cliente.open_by_key(
        SPREADSHEET_ID
    )

    return planilha


def converter_numero(valor):

    if valor is None:
        return 0

    valor = str(valor).strip()

    if not valor:
        return 0

    try:

        return float(
            valor.replace(",", ".")
        )

    except ValueError:

        return 0


def ler_planilha(planilha):

    dados = []

    abas = planilha.worksheets()

    for aba in abas:

        logger.info(
            f"Lendo aba: {aba.title}"
        )

        valores = aba.get_all_values()

        for numero_linha, linha in enumerate(
            valores[1:],
            start=2
        ):

            if len(linha) < COLUNA_ESTOQUE_MINIMO:
                continue

            codigo = linha[
                COLUNA_CODIGO - 1
            ].strip()

            if not codigo:
                continue

            estoque_atual = converter_numero(
                linha[
                    COLUNA_ESTOQUE_TOTAL - 1
                ]
            )

            estoque_minimo = converter_numero(
                linha[
                    COLUNA_ESTOQUE_MINIMO - 1
                ]
            )

            descricao = linha[COLUNA_DESCRICAO - 1].strip()

            dados.append({
                "aba": aba.title,
                "linha": numero_linha,
                "codigo": codigo,
                "descricao": descricao,
                "estoque_atual": estoque_atual,
                "estoque_minimo": estoque_minimo
            })

    return dados


def obter_ultima_atualizacao():

    caminho_log = (
        "logs/atualizacoes.log"
    )

    if not os.path.exists(caminho_log):

        return None

    with open(
        caminho_log,
        "r",
        encoding="utf-8"
    ) as arquivo:

        linhas = arquivo.readlines()

    for linha in reversed(linhas):

        if "ATUALIZAÇÃO CONCLUÍDA" in linha:

            data_texto = linha[:19]

            try:

                return datetime.strptime(
                    data_texto,
                    "%Y-%m-%d %H:%M:%S"
                )

            except ValueError:

                return None

    return None


def pode_enviar_email():

    os.makedirs(
        "data",
        exist_ok=True
    )

    if not os.path.exists(
        CAMINHO_ESTADO
    ):

        return True

    try:

        with open(
            CAMINHO_ESTADO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            estado = json.load(arquivo)

        ultimo_email = datetime.strptime(
            estado["ultimo_email"],
            "%Y-%m-%d %H:%M:%S"
        )

        agora = datetime.now()

        return (
            agora - ultimo_email
            >= timedelta(days=2)
        )

    except Exception:

        logger.exception(
            "Erro ao ler arquivo de estado"
        )

        return True


def registrar_email():

    os.makedirs(
        "data",
        exist_ok=True
    )

    estado = {

        "ultimo_email":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }

    with open(
        CAMINHO_ESTADO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            estado,
            arquivo,
            indent=4
        )


def enviar_email_erro(
    erro,
    ultima_atualizacao
):

    corpo = f"""
MONITORAMENTO DE ESTOQUE - ERRO

O sistema não conseguiu acessar ou
ler corretamente a planilha de estoque.

Data:
{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

Erro:
{erro}

Última atualização conhecida do estoque:
{
    ultima_atualizacao
    if ultima_atualizacao
    else "Não encontrada"
}

O monitoramento NÃO foi realizado.

Verifique:

- acesso à internet;
- Google Sheets;
- credenciais;
- permissões da planilha;
- execução do atualizador.
"""

    enviar_email(
        "🚨 ERRO - Monitoramento de Estoque Enjin",
        corpo
    )


def main():

    logger.info(
        "========================================"
    )

    logger.info(
        "INICIANDO MONITORAMENTO DE ESTOQUE"
    )

    logger.info(
        "========================================"
    )

    ultima_atualizacao = (
        obter_ultima_atualizacao()
    )

    try:

        planilha = conectar_google_sheets()

        logger.info(
            "Google Sheets acessado com sucesso"
        )

        dados = ler_planilha(
            planilha
        )

        logger.info(
            f"{len(dados)} itens analisados"
        )

    except Exception as erro:

        logger.exception(
            "ERRO AO ACESSAR GOOGLE SHEETS"
        )

        try:

            enviar_email_erro(
                erro,
                ultima_atualizacao
            )

            logger.info(
                "E-mail de erro enviado"
            )

        except Exception:

            logger.exception(
                "Não foi possível enviar "
                "o e-mail de erro"
            )

        return

    alertas = verificar_estoque(
        dados
    )

    logger.info(
        f"{len(alertas)} itens abaixo "
        f"do estoque mínimo"
    )

    if ultima_atualizacao:

        logger.info(
            "Última atualização do estoque: "
            + ultima_atualizacao.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

    else:

        logger.warning(
            "Última atualização do estoque "
            "não encontrada"
        )

    if not alertas:

        logger.info(
            "Nenhum item abaixo do mínimo"
        )

        logger.info(
            "MONITORAMENTO CONCLUÍDO"
        )

        return

    if not pode_enviar_email():

        logger.info(
            "Existem alertas, porém o "
            "último e-mail foi enviado "
            "há menos de 2 dias"
        )

        logger.info(
            "MONITORAMENTO CONCLUÍDO"
        )

        return

    ultima_atualizacao_texto = (
        ultima_atualizacao.strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        if ultima_atualizacao
        else "Não encontrada"
    )

    corpo = gerar_email_alerta(
        alertas,
        ultima_atualizacao_texto
    )

    try:

        enviar_email(
            (
                "⚠️ Monitoramento de Estoque - "
                f"{len(alertas)} itens abaixo do mínimo"
            ),
            corpo
        )

        registrar_email()

        logger.info(
            "E-mail de monitoramento enviado"
        )

    except Exception:

        logger.exception(
            "ERRO AO ENVIAR E-MAIL DE MONITORAMENTO"
        )

    logger.info(
        "MONITORAMENTO CONCLUÍDO"
    )


if __name__ == "__main__":
    main()