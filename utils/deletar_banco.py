import os
from dotenv import load_dotenv
from logs.logger import logger
from utils.conectar_banco_oracle import obter_conexao, liberar_conexao

# ==========================================
# CONFIGURAÇÕES (via .env)
# ==========================================
load_dotenv()

DOWNLOAD_DIR_EXCEL = os.getenv("DOWNLOAD_DIR_EXCEL")
DOWNLOAD_DIR_PDF = os.getenv("DOWNLOAD_DIR_PDF")

# ==========================================
# LIMPAR PASTA
# ==========================================
def limpar_pasta(caminho_pasta):
    logger.info("Limpando pasta: %s", caminho_pasta)

    if not os.path.exists(caminho_pasta):
        logger.warning("Pasta não existe. Criando: %s", caminho_pasta)
        os.makedirs(caminho_pasta)
        return

    arquivos = os.listdir(caminho_pasta)
    logger.info("Arquivos encontrados: %s", arquivos)

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(caminho_pasta, arquivo)
        if os.path.isfile(caminho_arquivo):
            os.remove(caminho_arquivo)
            logger.info("Arquivo removido: %s", arquivo)

    logger.info("Pasta limpa: %s", caminho_pasta)

# ==========================================
# DELETAR TABELA
# ==========================================
def deletar_tabela():
    logger.info("Conectando ao Oracle...")

    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        logger.info("Conexão estabelecida com sucesso.")

        logger.info("Deletando tabela LOTE...")
        cursor.execute("""
            BEGIN
                EXECUTE IMMEDIATE 'DROP TABLE lote';
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -942 THEN
                        RAISE;
                    END IF;
            END;
        """)
        conn.commit()
        logger.info("Tabela LOTE deletada com sucesso.")

    except Exception as e:
        logger.error("Erro ao deletar tabela: %s", e)
    finally:
        cursor.close()
        liberar_conexao(conn)
        logger.info("Conexão encerrada.")

# ==========================================
# PROCESSO COMPLETO
# ==========================================
def deletar_banco():
    logger.info("================================")
    logger.info("INICIANDO LIMPEZA")
    logger.info("================================")

    # 1 - Limpar Input
    limpar_pasta(DOWNLOAD_DIR_EXCEL)

    # 2 - Limpar NF
    limpar_pasta(DOWNLOAD_DIR_PDF)

    # 3 - Deletar tabela
    deletar_tabela()

    logger.info("================================")
    logger.info("LIMPEZA FINALIZADA")
    logger.info("================================")

if __name__ == "__main__":
    deletar_banco()
