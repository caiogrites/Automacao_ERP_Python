from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logs.logger import logger   # importa o logger centralizado

class LoginPage:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def login(self, username, password):
        logger.info("Iniciando processo de login...")

        try:
            username_field = self.wait.until(
                EC.visibility_of_element_located((By.ID, "email"))
            )
            logger.info("Campo de usuário encontrado.")

            password_field = self.wait.until(
                EC.visibility_of_element_located((By.ID, "password"))
            )
            logger.info("Campo de senha encontrado.")

            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
            )
            logger.info("Botão de login encontrado.")

            username_field.send_keys(username)
            logger.info("Usuário preenchido: %s", username)

            password_field.send_keys(password)
            logger.info("Senha preenchida (oculta).")

            login_button.click()
            logger.info("Botão de login clicado. Login enviado.")

        except Exception as e:
            logger.error("Erro durante o login: %s", e)
            raise
