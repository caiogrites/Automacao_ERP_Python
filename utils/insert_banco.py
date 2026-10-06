import os
import pandas as pd
from dotenv import load_dotenv
from logs.logger import logger
from utils.conectar_banco_oracle import obter_conexao, liberar_conexao

# ==========================================
# CONFIGURAÇÕES (via .env)
# ==========================================
load_dotenv()

PASTA_INPUT = os.getenv("DOWNLOAD_DIR_EXCEL")

# ==========================================
# INSERIR NO BANCO (Oracle)
# ==========================================
def inserir_banco():
    logger.info("Conectando ao Oracle...")

    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        logger.info("Conexão estabelecida com sucesso.")
    except Exception as e:
        logger.error("Erro ao conectar ao banco: %s", e)
        return

    arquivos = os.listdir(PASTA_INPUT)
    logger.info("Arquivos encontrados na pasta: %s", arquivos)

    for arquivo in arquivos:
        if not arquivo.startswith("BATCH-") or not arquivo.endswith("_PEDIDOS.csv"):
            logger.debug("Ignorando arquivo: %s", arquivo)
            continue

        logger.info("Processando arquivo: %s", arquivo)

        caminho_arquivo = os.path.join(PASTA_INPUT, arquivo)
        batch = arquivo.replace("_PEDIDOS.csv", "")

        try:
            df = pd.read_csv(caminho_arquivo, sep=";", encoding="utf-8")
            logger.info("Arquivo %s carregado com %d registros.", arquivo, len(df))
        except Exception as e:
            logger.error("Erro ao ler arquivo %s: %s", arquivo, e)
            continue

        for _, pedido in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO lote (
                        cliente, cpf_cnpj, email, cep, endereco,
                        cidade, estado, sku, produto, quantidade,
                        valor_unitario, desconto, frete, valor_total,
                        forma_pagamento, status, status_processamento,
                        order_id, batch
                    )
                    VALUES (
                        :1, :2, :3, :4, :5,
                        :6, :7, :8, :9, :10,
                        :11, :12, :13, :14, :15,
                        :16, :17, :18, :19
                    )
                """, (
                    pedido["Cliente"],
                    pedido["CPF/CNPJ"],
                    pedido["E-mail"],
                    pedido["CEP"],
                    pedido["Endereço"],
                    pedido["Cidade"],
                    pedido["Estado"],
                    pedido["SKU"],
                    pedido["Produto"],
                    pedido["Quantidade"],
                    pedido["Valor unitário"],
                    pedido["Desconto"],
                    pedido["Frete"],
                    pedido["Valor total"],
                    pedido["Forma de pagamento"],
                    pedido["Status"],
                    "PENDENTE",
                    pedido["Order ID"],
                    batch
                ))
                logger.info("Pedido inserido: Cliente=%s, Produto=%s", pedido["Cliente"], pedido["Produto"])
            except Exception as e:
                logger.error("Erro ao inserir pedido %s: %s", pedido.to_dict(), e)

        conn.commit()
        logger.info("BATCH inserido com sucesso: %s", batch)

    cursor.close()
    liberar_conexao(conn)
    logger.info("Todos os pedidos foram inseridos e conexão encerrada.")

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    inserir_banco()
