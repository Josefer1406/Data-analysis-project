import time
from optimizer import optimize
from config import SYMBOLS

def log(msg):
    print(f"[AUTO BOT] {msg}")

def run_cycle():

    log("Iniciando ciclo autónomo")

    for symbol in SYMBOLS:
        optimize(symbol)

    log("Ciclo terminado ✅")


if __name__ == "__main__":

    log("🤖 BOT AUTÓNOMO ACTIVADO")

    while True:

        try:
            run_cycle()

            # Espera 1 hora antes del siguiente análisis
            log("Esperando próximo ciclo...")
            time.sleep(3600)

        except Exception as e:
            log(f"Error: {e}")
            time.sleep(60)