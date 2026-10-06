import os
import pandas as pd
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from logs.logger import logger
from utils.conectar_banco_oracle import obter_conexao, liberar_conexao

class EmailRelatorio:
    def __init__(self):
        load_dotenv()
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.email_remetente = os.getenv("EMAIL_REMETENTE")
        self.email_destinatario = os.getenv("EMAIL_DESTINATARIO")
        self.email_senha = os.getenv("EMAIL_SENHA")
        self.caminho_arquivo = (
            r"C:\Users\User\Documents\AUTOMACAO_RPA\Input_Automacao\relatorio_lotes.xlsx"
        )

    def gerar_relatorio(self):
        logger.info("Conectando ao Oracle para gerar relatório...")
        conn = obter_conexao()
        query = "SELECT * FROM lote"
        df = pd.read_sql(query, conn)
        liberar_conexao(conn)
        logger.info("Consulta realizada com sucesso. Registros obtidos: %d", len(df))

        os.makedirs(os.path.dirname(self.caminho_arquivo), exist_ok=True)
        df.to_excel(self.caminho_arquivo, index=False)
        logger.info("📂 Relatório Excel gerado em: %s", self.caminho_arquivo)
        return self.caminho_arquivo

    def enviar_email(self):
        logger.info("Preparando e-mail para envio...")
        msg = EmailMessage()
        msg["Subject"] = "Relatório de Processamento ERP"
        msg["From"] = self.email_remetente
        msg["To"] = self.email_destinatario
        msg.set_content(
            "Olá Caio,\n\nSegue em anexo o relatório atualizado do processamento ERP.\n\nAtenciosamente,\nAutomação ERP"
        )

        with open(self.caminho_arquivo, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=os.path.basename(self.caminho_arquivo),
            )

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            logger.info("Conectando ao servidor SMTP...")
            server.login(self.email_remetente, self.email_senha)
            server.send_message(msg)
        logger.info("✅ E-mail enviado com sucesso para %s", self.email_destinatario)

if __name__ == "__main__":
    relatorio = EmailRelatorio()
    relatorio.gerar_relatorio()
    relatorio.enviar_email()
