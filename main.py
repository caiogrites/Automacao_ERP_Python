import os
from dotenv import load_dotenv
from utils.driver import create_driver
from pages.login_page import LoginPage
from pages.batches_page import BatchesPage
from pages.download_notas import NotasPage   # classe NotasPage
from pages.enviar_email import EmailRelatorio  # classe EmailRelatorio
from utils.deletar_banco import deletar_banco
from utils.criar_banco import criar_banco
from utils.insert_banco import inserir_banco
from pages.nova_nota_page import processar_pedidos
from utils.conectar_banco_oracle import iniciar_pool, fechar_pool
from logs.logger import logger

# Carrega variáveis do .env
load_dotenv()

URL = os.getenv("URL")
USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")
DOWNLOAD_DIR_EXCEL = os.getenv("DOWNLOAD_DIR_EXCEL")
DOWNLOAD_DIR_PDF = os.getenv("DOWNLOAD_DIR_PDF")

def main():
    logger.info("================================")
    logger.info("INICIANDO AUTOMAÇÃO ERP")
    logger.info("================================")

    iniciar_pool()
    deletar_banco()

    try:
        # Fluxo Excel
        driver_excel = create_driver(DOWNLOAD_DIR_EXCEL)
        driver_excel.get(URL)
        LoginPage(driver_excel).login(USUARIO, SENHA)
        BatchesPage(driver_excel).processar_lotes()
        driver_excel.quit()

        criar_banco()
        inserir_banco()

        # Fluxo PDF
        driver_pdf = create_driver(DOWNLOAD_DIR_PDF)
        driver_pdf.get(URL)
        LoginPage(driver_pdf).login(USUARIO, SENHA)
        processar_pedidos(driver_pdf)

        notas_page = NotasPage(driver_pdf)
        notas_page.baixar_notas_pdf()
        driver_pdf.quit()

        # Envio de relatório
        logger.info("Gerando relatório Excel e enviando por e-mail...")
        email_relatorio = EmailRelatorio()
        arquivo = email_relatorio.gerar_relatorio()
        email_relatorio.enviar_email()
        logger.info("Relatório enviado com sucesso!")

        logger.info("================================")
        logger.info("AUTOMAÇÃO FINALIZADA")
        logger.info("================================")

    except Exception as erro:
        logger.error("================================")
        logger.error("ERRO NA AUTOMAÇÃO")
        logger.error("================================")
        logger.error("Detalhes do erro: %s", erro)

    finally:
        fechar_pool()

if __name__ == "__main__":
    main()
