import oracledb
import os
from core.config import DB_USER_W, DB_USER_R, DB_PASS_W, DB_PASS_R, DB_DSN, ORACLE_CLIENT_LIB

def get_connection( modo_execucao ):
    if os.name == "nt":
        oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_LIB)

    if modo_execucao == 'write':
        user=DB_USER_W
        password=DB_PASS_W
    elif modo_execucao == 'read':
        user=DB_USER_R
        password=DB_PASS_R
    else:
        user=''
        password=''

    return oracledb.connect(
        user=user,
        password=password,
        dsn=DB_DSN
    )