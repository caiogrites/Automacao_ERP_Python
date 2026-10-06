from flask import Flask, request, jsonify
import subprocess
import logging
import threading
import sys

app = Flask(__name__)

# Logger centralizado
logger = logging.getLogger("RPA_WEBHOOK")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("rpa_webhook.log", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_process_output(process):
    """Captura stdout/stderr do main.py em threads separadas"""
    def reader(stream, level):
        for line in iter(stream.readline, b''):
            logger.log(level, line.decode("utf-8", errors="ignore").strip())
        stream.close()

    threading.Thread(target=reader, args=(process.stdout, logging.INFO), daemon=True).start()
    threading.Thread(target=reader, args=(process.stderr, logging.ERROR), daemon=True).start()


@app.route("/webhook/rpa/batch-ready", methods=["POST"])
def batch_ready():
    dados = request.get_json(silent=True)
    logger.info("Webhook recebido com dados: %s", dados)

    try:
        # Usa o mesmo Python do venv que roda o Flask
        process = subprocess.Popen(
            [sys.executable, r"C:\Projetos\automacao_web\main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info("main.py iniciado em background. PID: %s", process.pid)

        # Threads para capturar saída sem travar
        log_process_output(process)

        return jsonify({
            "status": "success",
            "message": "main.py iniciado em background",
            "pid": process.pid
        }), 202

    except Exception as e:
        logger.error("Falha ao iniciar main.py: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "online"}), 200


if __name__ == "__main__":
    logger.info("================================")
    logger.info("RPA WEBHOOK ONLINE")
    logger.info("Health: http://192.168.0.220:5000/health")
    logger.info("Webhook: POST http://192.168.0.220:5000/webhook/rpa/batch-ready")
    logger.info("================================")

    app.run(host="0.0.0.0", port=5000, debug=False)
