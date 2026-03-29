import time

from services.scanner import escanear_mercado
from core.risk import calcular_size

print("🤖 BOT PROFESIONAL INICIADO")

while True:

    try:

        oportunidades = escanear_mercado()

        for symbol, precio in oportunidades:

            size = calcular_size(precio)

            print(f"🚀 Oportunidad detectada")
            print(symbol, precio, size)

        print("⏳ Esperando próximo ciclo...")
        time.sleep(300)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(60)