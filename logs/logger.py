# logs/logger.py
import logging
import os
import sys

LOG_DIR = r"C:\Projetos\automacao_web\logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "automacao.log")

# Handler para arquivo (modo "w" recria o arquivo a cada execução)
file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))

# Handler para console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logger = logging.getLogger("AutomacaoRPA")
logger.setLevel(logging.INFO)

# Evita duplicação de handlers
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
