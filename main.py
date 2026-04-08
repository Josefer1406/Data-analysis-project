import time
import config
from services.scanner import analizar
from portfolio import Portfolio

bot = Portfolio()

print("🤖 BOT CUANT INSTITUCIONAL PRO ACTIVO")

while True:

    try:
        signals = []
        precios = {}

        # =========================
        # SCAN
        # =========================
        for symbol in config.CRYPTOS:

            data = analizar(symbol)

            if data:
                signals.append(data)
                precios[symbol] = data["precio"]

        # =========================
        # ORDENAR
        # =========================
        signals = sorted(signals, key=lambda x: x["prob"], reverse=True)

        # =========================
        # GESTIÓN POSICIONES
        # =========================
        bot.actualizar(precios)

        # =========================
        # APERTURA
        # =========================
        for s in signals:
            bot.abrir(s)

        # =========================
        # ESTADO
        # =========================
        print(f"\n💰 Capital: {bot.capital}")
        print(f"📊 Posiciones: {list(bot.posiciones.keys())}")

        time.sleep(config.COOLDOWN_BASE)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        time.sleep(10)