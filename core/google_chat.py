from __future__ import annotations

from typing import Iterable

import requests

from core.config import SETTINGS
from core.logger import logger


def enviar_alerta_google_chat(alertas: Iterable[object], url_planilha: str) -> None:
    if not SETTINGS.google_chat_webhook_url:
        logger.warning("Webhook do Google Chat não configurado; alerta no Chat ignorado.")
        return
    linhas = [f"• {a.aba} | *{a.codigo}*: atual {a.estoque_atual:g} / mínimo {a.estoque_minimo:g}" for a in alertas]
    resposta = requests.post(SETTINGS.google_chat_webhook_url, json={"text": "*Alerta de estoque mínimo*\n\n" + "\n".join(linhas) + f"\n\n[Ver planilha]({url_planilha})"}, timeout=30)
    resposta.raise_for_status()
    logger.info("Alerta enviado ao Google Chat")
