import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logs.logger import logger
from utils.conectar_banco_oracle import obter_conexao, liberar_conexao

class NotasPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def atualizar_status_por_cliente(self, status,cliente, valor_limpo):
        conn = None
        cursor = None
        try:
            conn = obter_conexao()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lote
                SET status_processamento = :1
                WHERE cliente = :2 AND VALOR_TOTAL = :3
            """, (status, cliente, valor_limpo))
            conn.commit()
            logger.info("Status atualizado para cliente=%s, Status=%s", cliente, status)
        except Exception as e:
            logger.error("Erro ao atualizar status para cliente %s: %s", cliente, e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                liberar_conexao(conn)

    def acessar_aba_notas(self):
        aba_notas = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/aside/nav/div[2]/div[2]/a[4]"))
        )
        aba_notas.click()
        logger.info("Aba de Notas acessada com sucesso.")

    def baixar_notas_pdf(self):
        self.acessar_aba_notas()

        try:
            linhas = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//table/tbody/tr"))
            )
            logger.info("Total de notas encontradas na tela: %d", len(linhas))
        except Exception:
            logger.warning("Nenhuma nota encontrada após aguardar o carregamento.")
            return

        for linha in linhas:
            try:
                cliente = linha.find_element(By.XPATH, "./td[3]").text.strip()
                numero_nf = linha.find_element(By.XPATH, "./td[2]").text.strip()
                valor = linha.find_element(By.XPATH, "./td[6]").text.strip()
                valor_limpo = valor.replace("R$", "").replace(".", "").strip()

                # Se terminar com ",00", remove
                if valor_limpo.endswith(",00"):
                   valor_limpo = valor_limpo[:-3]

                logger.info("Processando nota %s para cliente %s", numero_nf, cliente)

                botao_pdf = linha.find_element(By.XPATH, ".//button[@title='Baixar PDF']")
                self.wait.until(EC.element_to_be_clickable(botao_pdf))
                botao_pdf.click()
                logger.info("Download PDF iniciado para %s", numero_nf)
                time.sleep(3)

                self.atualizar_status_por_cliente(cliente, valor_limpo, "NOTA EMITIDA")
                logger.info("✅ Nota %s baixada e status atualizado para cliente %s", numero_nf, cliente, valor_limpo)

            except Exception as e:
                logger.error("❌ Falha ao baixar nota para cliente %s: %s", cliente, e)
                self.atualizar_status_por_cliente(cliente, "ERRO_DOWNLOAD")
