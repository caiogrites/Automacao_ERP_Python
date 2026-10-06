import os
import sys
# Ajusta o path para permitir import de módulos no nível raiz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import oracledb
from dotenv import load_dotenv
from logs.logger import logger


# Carrega variáveis do .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_SERVICE = os.getenv("DB_SERVICE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

connection_pool = None

def iniciar_pool(minconn=1, maxconn=5):
    global connection_pool
    if connection_pool is None:
        dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
        connection_pool = oracledb.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=dsn,
            min=minconn,
            max=maxconn,
            increment=1
        )
        logger.info("✅ Pool de conexões Oracle inicializado com sucesso.")

def obter_conexao():
    if connection_pool is None:
        iniciar_pool()
    return connection_pool.acquire()

def liberar_conexao(conn):
    conn.close()  # devolve ao pool

def fechar_pool():
    if connection_pool:
        connection_pool.close()
        logger.info("🔒 Pool de conexões Oracle fechado.")

if __name__ == "__main__":
    # Inicializa o pool
    iniciar_pool()

    # Pega uma conexão
    conn = obter_conexao()
    cursor = conn.cursor()

    # Teste simples
    cursor.execute("SELECT * FROM dual")
    print(cursor.fetchall())

    # Libera recursos
    cursor.close()
    liberar_conexao(conn)
    fechar_pool()