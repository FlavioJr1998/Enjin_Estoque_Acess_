import logging
import os

def criar_logger(nome, arquivo):

    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(nome)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = logging.FileHandler(
        f"logs/{arquivo}",
        encoding="utf-8"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
