import time
import config
import portfolio
from ml import model

UNIVERSO = [
    "BTC/USDT","ETH/USDT","SOL/USDT",
    "ADA/USDT","XRP/USDT","AVAX/USDT",
    "LINK/USDT","ATOM/USDT"
]

def run_bot():
    print("🚀 BOT CUANT INSTITUCIONAL PRO (POSITION SIZING)")

    while True:
        print("\n🔎 Analizando mercado...")

        señales = []

        for symbol in UNIVERSO:
            data = model.analizar_activo(symbol)

            print(f"{symbol} | score: {data['score']} | prob: {data['probabilidad']}")

            if data["score"] >= config.MIN_SCORE:
                señales.append(data)

        señales.sort(key=lambda x: x["probabilidad"], reverse=True)

        entradas = 0

        for s in señales:
            if entradas >= config.MAX_ENTRADAS_POR_CICLO:
                break

            if portfolio.puede_comprar(s["symbol"]):
                portfolio.abrir_posicion(
                    s["symbol"],
                    s["probabilidad"],
                    s["precio"]
                )
                entradas += 1

        portfolio.gestionar_riesgo()
        portfolio.actualizar_cooldowns()
        portfolio.estado()

        print("⏳ Ciclo completado...\n")
        time.sleep(10)

if __name__ == "__main__":
    run_bot()