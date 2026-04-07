import time
import config
import portfolio
from ml import model  # ✅ IMPORT CORRECTO

UNIVERSO = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT",
    "ADA/USDT", "XRP/USDT", "AVAX/USDT",
    "LINK/USDT", "ATOM/USDT"
]

def filtrar_correlacion(señales):
    """
    Simulación simple: evita sobrecargar el portafolio
    """
    return señales[:config.MAX_POSICIONES]

def run_bot():
    print("🚀 BOT CUANT INSTITUCIONAL PRO")

    while True:
        print("\n🔎 Analizando mercado...")

        señales = []

        for symbol in UNIVERSO:
            data = model.analizar_activo(symbol)

            print(f"{symbol} | score: {data['score']} | prob: {data['probabilidad']}")

            if data["score"] >= config.MIN_SCORE:
                señales.append(data)

        # Ordenar por mejor señal
        señales.sort(key=lambda x: x["probabilidad"], reverse=True)

        # Filtro anticorrelación
        señales = filtrar_correlacion(señales)

        # Ejecución
        for s in señales:
            if s["probabilidad"] >= config.UMBRAL_COMPRA:
                if portfolio.puede_comprar(s["symbol"]):
                    portfolio.abrir_posicion(s["symbol"], s["probabilidad"])

        # Gestión de riesgo
        portfolio.gestionar_riesgo()

        # Cooldowns
        portfolio.actualizar_cooldowns()

        # Estado
        portfolio.estado()

        print("⏳ Ciclo completado...\n")
        time.sleep(10)

if __name__ == "__main__":
    run_bot()