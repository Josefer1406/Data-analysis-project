import time
import scanner
import risk
import config

print("🤖 BOT PROFESIONAL INICIADO")

while True:

    print("\n[AUTO BOT] Iniciando ciclo autónomo")

    oportunidades = scanner.escanear_mercado()

    for trade in oportunidades:

        symbol = trade["symbol"]
        precio = trade["precio"]

        size = risk.calcular_size(precio)

        print(f"✅ Señal detectada -> {symbol}")
        print(f"Precio: {precio}")
        print(f"Tamaño posición: {size}")

    print("[AUTO BOT] Esperando próximo ciclo...")

    time.sleep(config.INTERVALO_CICLO)