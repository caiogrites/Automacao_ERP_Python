import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logs.logger import logger

class BatchesPage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

        # Diretório de download para Excel
        self.diretorio_download = r"C:\Users\User\Documents\AUTOMACAO_RPA\Input_Automacao"
        os.makedirs(self.diretorio_download, exist_ok=True)

        # Configura o Chrome para realizar os downloads
        self.configurar_diretorio_download()

    def configurar_diretorio_download(self):
        self.driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": self.diretorio_download
            }
        )
        logger.info("Diretório de download configurado para Excel: %s", self.diretorio_download)

    def scroll_ate_elemento(self, locator):
        """Rola até o elemento alvo e retorna o objeto WebElement"""
        elemento = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
        time.sleep(0.5)
        return elemento

    def safe_click(self, locator):
        """Scroll até o elemento e tenta clicar, com fallback via JS"""
        elemento = self.scroll_ate_elemento(locator)
        try:
            elemento.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", elemento)
            logger.info("Clique realizado via JavaScript como fallback.")

    def clicar_lotes(self):
        logger.info("Abrindo página de Lotes...")
        self.safe_click((By.XPATH, "//a[@href='/lotes']"))
        logger.info("Página de Lotes aberta")

        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[starts-with(normalize-space(), 'BATCH-')]"))
        )
        logger.info("Lista de lotes carregada")

    def listar_lotes(self):
        elementos = self.driver.find_elements(By.XPATH, "//span[starts-with(normalize-space(), 'BATCH-')]")
        lotes = []
        for elemento in elementos:
            batch = elemento.text.strip()
            if batch and batch not in lotes:
                lotes.append(batch)
        logger.info("Lotes encontrados: %s", lotes)
        return lotes

    def selecionar_lote(self, batch):
        logger.info("Selecionando %s...", batch)
        self.safe_click(
            (By.XPATH, f"//span[normalize-space()='{batch}']/ancestor::div[contains(@class, 'cursor-pointer')]")
        )
        logger.info("%s selecionado", batch)

    def exportar_excel(self):
        logger.info("Procurando botão Exportar Excel...")
        self.safe_click((By.XPATH, "//button[contains(., 'Exportar Excel')]"))
        logger.info("Botão Exportar Excel clicado")

        time.sleep(3)
        logger.info("Download do Excel realizado. Arquivo salvo em: %s", self.diretorio_download)

    def carregar_mais_lotes(self):
        """Scroll até o último lote visível para forçar carregamento de novos"""
        elementos = self.driver.find_elements(By.XPATH, "//span[starts-with(normalize-space(), 'BATCH-')]")
        if elementos:
            ultimo = elementos[-1]
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", ultimo)
            time.sleep(1)
            logger.info("Scroll realizado até o último lote.")

    def processar_lotes(self):
        logger.info("================================")
        logger.info("INICIANDO PROCESSAMENTO DE LOTES")
        logger.info("================================")

        self.clicar_lotes()
        processados = set()

        while True:
            logger.info("--------------------------------")
            logger.info("BUSCANDO PRÓXIMO BATCH")
            logger.info("--------------------------------")

            lotes = self.listar_lotes()
            pendentes = [batch for batch in lotes if batch not in processados]

            if not pendentes:
                logger.info("================================")
                logger.info("NÃO HÁ MAIS LOTES PENDENTES")
                logger.info("================================")
                break

            batch = pendentes[0]
            logger.info("--------------------------------")
            logger.info("PROCESSANDO: %s", batch)
            logger.info("--------------------------------")

            self.selecionar_lote(batch)
            self.exportar_excel()
            processados.add(batch)

            logger.info("--------------------------------")
            logger.info("%s FINALIZADO", batch)
            logger.info("Total processado: %d", len(processados))
            logger.info("--------------------------------")

            # Scroll dinâmico a cada 3 lotes processados
            if len(processados) % 3 == 0:
                self.carregar_mais_lotes()

        logger.info("================================")
        logger.info("TODOS OS LOTES FORAM PROCESSADOS")
        logger.info("Total de lotes: %d", len(processados))
        logger.info("================================")
