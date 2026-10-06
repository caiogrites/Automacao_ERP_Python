from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def create_driver(pasta_download: str):
    """
    Cria um driver configurado para baixar arquivos em um diretório específico.
    """
    options = Options()
    options.add_experimental_option("detach", True)

    os.makedirs(pasta_download, exist_ok=True)

    prefs = {
        "download.default_directory": pasta_download,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver
