import os
from dotenv import load_dotenv

load_dotenv()

ORACLE_CLIENT_LIB = os.getenv("ORACLE_CLIENT_LIB")

EMPRESA = int(os.getenv("EMPRESA", 2))

DATA_INICIO_TESTE = "10/04/2026"
DATA_FIM_TESTE = "12/04/2026"
INTERVALO_HORAS = 6

DB_USER_R = os.getenv("DB_USER_R")
DB_PASS_R = os.getenv("DB_PASS_R")
DB_USER_W = os.getenv("DB_USER_W")
DB_PASS_W = os.getenv("DB_PASS_W")

if os.getenv('AMBIENTE_DESCRICAO') == 'PRODUCAO':
    AMBIENTE_DESCRICAO = 'PRODUÇÃO'
    DB_DSN = os.getenv("DB_DSN_PROD")
else:
    DB_DSN = os.getenv("DB_DSN_HOMO")


