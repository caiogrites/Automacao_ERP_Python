# tests/button_teste.py
import os
import pytest
import pandas as pd
from pages.enviar_email import gerar_relatorio, enviar_email
from logs.logger import logger

def test_gerar_relatorio_cria_excel():
    """Valida se o relatório Excel é gerado e contém dados"""
    caminho = gerar_relatorio()
    logger.info("Verificando se o arquivo Excel foi criado: %s", caminho)
    assert os.path.exists(caminho), f"Arquivo {caminho} não foi gerado"

    df = pd.read_excel(caminho)
    logger.info("Linhas encontradas no relatório: %d", len(df))
    assert len(df) > 0, "Relatório gerado está vazio"

def test_enviar_email_monta_mensagem(monkeypatch, tmp_path):
    """Valida se o e-mail é montado corretamente sem envio real"""
    caminho_fake = tmp_path / "fake.xlsx"
    caminho_fake.write_text("conteudo de teste")

    enviado = {}

    def fake_send_message(self, msg):
        enviado["subject"] = msg["Subject"]
        enviado["to"] = msg["To"]
        enviado["from"] = msg["From"]
        # Confirma que o anexo está presente
        anexos = [part.get_filename() for part in msg.iter_attachments()]
        logger.info("Anexos encontrados na mensagem: %s", anexos)
        assert "fake.xlsx" in anexos

    def fake_login(self, user, password):
        logger.info("Login SMTP simulado para usuário %s", user)
        return True

    # substitui métodos reais por fakes
    monkeypatch.setattr("smtplib.SMTP.send_message", fake_send_message)
    monkeypatch.setattr("smtplib.SMTP.login", fake_login)

    enviar_email(str(caminho_fake))

    logger.info("Validando montagem da mensagem de e-mail")
    assert enviado["subject"] == "Relatório de Processamento ERP"
    assert enviado["to"] == "caio.grites@zohomail.com"
    assert enviado["from"] == "caiogrites@gmail.com"
