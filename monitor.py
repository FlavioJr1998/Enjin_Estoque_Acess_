from datetime import datetime
import json
import os

def verificar_estoque(dados):

    alertas = []

    for item in dados:

        codigo = item["codigo"]
        estoque_atual = item["estoque_atual"]
        estoque_minimo = item["estoque_minimo"]

        if estoque_atual < estoque_minimo:

            alerta = item.copy()

            alerta["deficit"] = (
                estoque_minimo - estoque_atual
            )

            alertas.append(alerta)

    return alertas

def gerar_email_alerta(
    alertas,
    ultima_atualizacao
):

    corpo = []

    corpo.append(
        "MONITORAMENTO DE ESTOQUE - ENJIN"
    )

    corpo.append("")
    corpo.append(
        "Data da verificação: "
        + agora()
    )

    corpo.append(
        "Última atualização do estoque: "
        + ultima_atualizacao
    )

    corpo.append("")

    corpo.append(
        f"Itens abaixo do estoque mínimo: "
        f"{len(alertas)}"
    )

    corpo.append("")
    corpo.append("=" * 70)

    for alerta in alertas:

        corpo.append(f"Código: {alerta['codigo']}")
        corpo.append(f"Descrição: {alerta['descricao']}")
        corpo.append(f"Aba: {alerta['aba']}")
        corpo.append(f"Linha: {alerta['linha']}")
        corpo.append(f"Estoque atual: {alerta['estoque_atual']}")
        corpo.append(f"Estoque mínimo: {alerta['estoque_minimo']}")
        corpo.append(f"Déficit: {alerta['deficit']}")

        corpo.append("=" * 70)

    return "\n".join(corpo)


def agora():

    from datetime import datetime

    return datetime.now().strftime(
        "%d/%m/%Y %H:%M:%S"
    )