import time
import config
from services import scanner
from filters.market_filter import mercado_favorable
from core import risk

print("🤖 BOT HEDGE FUND INICIADO")


while True:

    try:

        # =========================
        # FILTRO GLOBAL
        # =========================
        if not mercado_favorable():
            print("⏳ Mercado no favorable")
            time.sleep(300)
            continue

        # =========================
        # SCANNER
        # =========================
        oportunidades = scanner.escanear_mercado()

        if not oportunidades:
            print("Sin oportunidades")
        else:
            print("🔥 Oportunidades detectadas:")

            for symbol, precio in oportunidades:

                size = risk.calcular_size(precio)

                print(
                    f"TRADE -> {symbol} | Precio {precio} | Size {size}"
                )

        print("⏳ Esperando próximo ciclo...")
        time.sleep(300)

    except Exception as e:
        print(f"Error general: {e}")
        time.sleep(60)