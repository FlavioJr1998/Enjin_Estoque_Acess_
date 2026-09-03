import os
import smtplib

from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


def enviar_email(assunto, corpo):

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")

    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    if not all([
        smtp_host,
        email_from,
        email_to,
        email_user,
        email_pass
    ]):
        raise ValueError(
            "Configurações de e-mail incompletas no .env"
        )

    mensagem = EmailMessage()

    mensagem["Subject"] = assunto
    mensagem["From"] = email_from
    mensagem["To"] = email_to

    mensagem.set_content(corpo)

    with smtplib.SMTP(
        smtp_host,
        smtp_port,
        timeout=30
    ) as servidor:

        servidor.starttls()

        servidor.login(
            email_user,
            email_pass
        )

        servidor.send_message(mensagem)