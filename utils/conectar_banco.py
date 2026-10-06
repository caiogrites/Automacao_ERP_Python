import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os
from logs.logger import logger

# Carrega variáveis do .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

connection_pool = None

def iniciar_pool(minconn=1, maxconn=5):
    global connection_pool
    if connection_pool is None:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn, maxconn,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("✅ Pool de conexões inicializado com sucesso.")

def obter_conexao():
    if connection_pool is None:
        iniciar_pool()
    return connection_pool.getconn()

def liberar_conexao(conn):
    connection_pool.putconn(conn)

def fechar_pool():
    if connection_pool:
        connection_pool.closeall()
        logger.info("🔒 Pool de conexões fechado.")
