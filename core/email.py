from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Iterable

from core.config import SETTINGS
from core.logger import logger


def enviar_alerta_email(alertas: Iterable[object], url_planilha: str) -> None:
    if not (SETTINGS.smtp_host and SETTINGS.email_from and SETTINGS.email_to):
        logger.warning("E-mail não configurado; alerta por e-mail ignorado.")
        return
    linhas = [f"- {a.aba} | Código {a.codigo}: atual {a.estoque_atual:g}, mínimo {a.estoque_minimo:g}" for a in alertas]
    mensagem = EmailMessage()
    mensagem["Subject"] = f"Alerta de estoque mínimo: {len(linhas)} item(ns)"
    mensagem["From"] = SETTINGS.email_from
    mensagem["To"] = ", ".join(SETTINGS.email_to)
    mensagem.set_content("Itens abaixo do estoque mínimo:\n\n" + "\n".join(linhas) + f"\n\nPlanilha: {url_planilha}")
    with smtplib.SMTP(SETTINGS.smtp_host, SETTINGS.smtp_port, timeout=30) as smtp:
        smtp.starttls()
        if SETTINGS.email_user and SETTINGS.email_pass:
            smtp.login(SETTINGS.email_user, SETTINGS.email_pass)
        smtp.send_message(mensagem)
    logger.info("Alerta enviado por e-mail para %s destinatário(s)", len(SETTINGS.email_to))
