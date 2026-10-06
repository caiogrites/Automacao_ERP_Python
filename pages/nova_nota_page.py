from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logs.logger import logger
from utils.conectar_banco_oracle import obter_conexao, liberar_conexao

class EmitirNotaException(Exception):
    pass

class NovaNotaPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

        # Inputs
        self.botao_nova_nota = (By.CSS_SELECTOR, 'a[href="/erp/nova-nota"]')
        self.campo_cliente = (By.XPATH, "//input[@placeholder='Pesquisar cliente por nome ou CPF/CNPJ...']")
        self.campo_produto = (By.XPATH, "//input[@placeholder='Pesquisar produto por SKU ou descrição...']")
        self.campo_quantidade = (By.CSS_SELECTOR, "input[type='number'][min='1']")
        self.campo_desconto = (By.XPATH, "//label[normalize-space()='Desconto']/following-sibling::input")
        self.campo_frete = (By.XPATH, "//label[normalize-space()='Frete']/following-sibling::input")
        self.botao_emitir = (By.XPATH, "//button[contains(normalize-space(.), 'EMITIR NOTA')]")
        self.mensagem_sucesso = (By.XPATH, "//*[contains(normalize-space(.), 'NOTA EMITIDA COM SUCESSO')]")

        # Sugestões logo abaixo dos inputs
        self.card_cliente = (By.XPATH, "/html/body/div[1]/div[1]/div/main/div/div[2]/div/div[1]/div[2]/button")
        self.card_produto = (By.XPATH, "/html/body/div[1]/div[1]/div/main/div/div[2]/div/div[3]/div[2]/button")

    def clicar_nova_nota(self):
        logger.info("Abrindo nova nota fiscal...")
        botao = self.wait.until(EC.element_to_be_clickable(self.botao_nova_nota))
        botao.click()
        logger.info("Nova Nota Fiscal aberta.")

    def preencher_cliente(self, nome_cliente):
        logger.info("Preenchendo cliente: %s", nome_cliente)
        campo = self.wait.until(EC.visibility_of_element_located(self.campo_cliente))
        campo.click()
        campo.send_keys(Keys.CONTROL, "a")
        campo.send_keys(nome_cliente)
        card = self.wait.until(EC.element_to_be_clickable(self.card_cliente))
        self.driver.execute_script("arguments[0].click();", card)
        logger.info("Cliente selecionado: %s", nome_cliente)

    def preencher_produto(self, nome_produto):
        logger.info("Preenchendo produto: %s", nome_produto)
        campo = self.wait.until(EC.visibility_of_element_located(self.campo_produto))
        campo.click()
        campo.send_keys(Keys.CONTROL, "a")
        campo.send_keys(nome_produto)
        card = self.wait.until(EC.element_to_be_clickable(self.card_produto))
        self.driver.execute_script("arguments[0].click();", card)
        logger.info("Produto selecionado: %s", nome_produto)

    def preencher_quantidade(self, quantidade):
        logger.info("Preenchendo quantidade: %s", quantidade)
        campo = self.wait.until(EC.visibility_of_element_located(self.campo_quantidade))
        campo.click()
        campo.send_keys(Keys.CONTROL, "a")
        campo.send_keys(str(quantidade))
        campo.send_keys(Keys.TAB)
        logger.info("Quantidade preenchida: %s", quantidade)

    def preencher_valor(self, locator, valor, descricao):
        logger.info("Preenchendo %s: %s", descricao, valor)
        campo = self.wait.until(EC.visibility_of_element_located(locator))
        self.driver.execute_script(
            """
            const campo = arguments[0];
            const valor = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(campo, valor);
            campo.dispatchEvent(new Event('input', { bubbles: true }));
            campo.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            campo,
            str(valor)
        )
        campo.send_keys(Keys.TAB)
        logger.info("%s preenchido: %s", descricao, valor)

    def preencher_desconto(self, valor):
        self.preencher_valor(self.campo_desconto, valor, "desconto")

    def preencher_frete(self, valor):
        self.preencher_valor(self.campo_frete, valor, "frete")

    def emitir_nota(self):
        logger.info("Emitindo nota fiscal...")
        botao_emitir = self.wait.until(EC.element_to_be_clickable(self.botao_emitir))
        botao_emitir.click()
        logger.info("Botão 'EMITIR NOTA' clicado.")

        try:
            self.wait.until(EC.visibility_of_element_located(self.mensagem_sucesso))
            logger.info("Nota emitida com sucesso!")
        except Exception as e:
            logger.error("Erro ao emitir nota fiscal: %s", e)
            raise EmitirNotaException("Erro ao emitir nota fiscal.")

        # Atualiza página (F5)
        self.driver.refresh()
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        logger.info("Página atualizada após emissão.")

# Funções de banco (Oracle)
def buscar_pedidos_pendentes():
    logger.info("Buscando pedidos pendentes no banco...")
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, cliente, produto, quantidade, desconto, frete
        FROM lote
        WHERE status_processamento = 'PENDENTE'
    """)
    pedidos = cursor.fetchall()
    cursor.close()
    liberar_conexao(conn)
    logger.info("Total de pedidos pendentes encontrados: %d", len(pedidos))
    return pedidos

def atualizar_status(cliente, produto, status):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE lote
        SET status_processamento = :1
        WHERE cliente = :2
          AND produto = :3
    """, (status, cliente, produto))
    conn.commit()
    cursor.close()
    liberar_conexao(conn)
    logger.info("Status atualizado: Cliente=%s, Produto=%s, Status=%s", cliente, produto, status)


def processar_pedidos(driver):
    nova_nota_page = NovaNotaPage(driver)
    for order_id, cliente, produto, quantidade, desconto, frete in buscar_pedidos_pendentes():
        try:
            nova_nota_page.clicar_nova_nota()
            nova_nota_page.preencher_cliente(cliente)
            nova_nota_page.preencher_produto(produto)
            nova_nota_page.preencher_quantidade(quantidade)
            nova_nota_page.preencher_desconto(desconto)
            nova_nota_page.preencher_frete(frete)
            nova_nota_page.emitir_nota()

            atualizar_status(cliente, produto, "NOTA EMITIDA")
            logger.info("✅ Nota emitida com sucesso para %s - %s", cliente, produto)
        except Exception as e:
            atualizar_status(cliente, produto, "PRODUTO NÃO ENCONTRADO")
            logger.error("❌ Falha ao emitir nota para %s - %s: %s", cliente, produto, e)
