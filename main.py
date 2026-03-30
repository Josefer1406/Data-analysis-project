import time
import config

from filters.market_filter import mercado_favorable
from services.scanner import analizar
from core.risk import calcular_size

import portfolio
import logger

print("🤖 BOT EXPERTO MULTI-TRADE INICIADO")

while True:

    try:
        # =========================
        # 1. FILTRO GLOBAL
        # =========================
        if not mercado_favorable():
            print("⛔ Mercado no favorable")
            time.sleep(config.CYCLE_TIME)
            continue

        # =========================
        # 2. ANALIZAR TODAS LAS CRYPTOS
        # =========================
        ranking = []

        for symbol in config.CRYPTOS:
            try:
                score, precio = analizar(symbol)
                ranking.append((symbol, score, precio))
            except Exception as e:
                print(f"Error analizando {symbol}: {e}")

        # =========================
        # 3. ORDENAR POR SCORE
        # =========================
        ranking.sort(key=lambda x: x[1], reverse=True)

        # =========================
        # 4. MOSTRAR TOP
        # =========================
        top_cryptos = ranking[:config.MAX_POSICIONES]

        print("\n🏆 Top oportunidades:")

        for symbol, score, precio in top_cryptos:
            print(f"{symbol} | Score {score} | Precio {precio}")

        # =========================
        # 5. GESTIÓN DE POSICIONES (SALIDAS)
        # =========================
        for symbol in list(portfolio.posiciones.keys()):
            try:
                # usamos el precio más reciente del ranking
                precio_actual = next(
                    (p for s, sc, p in ranking if s == symbol),
                    None
                )

                if precio_actual is None:
                    continue

                if portfolio.evaluar_salida(symbol, precio_actual):
                    pnl = portfolio.cerrar_posicion(symbol, precio_actual)
                    logger.log_trade(symbol, "SELL", precio_actual, 0, pnl)
                    print(f"🔴 Cierre {symbol} | PnL: {pnl}")

            except Exception as e:
                print(f"Error cierre {symbol}: {e}")

        # =========================
        # 6. ENTRADAS (MULTI-TRADE)
        # =========================
        for symbol, score, precio in top_cryptos:

            try:
                if score >= 2:

                    size = calcular_size(precio)

                    if portfolio.abrir_posicion(symbol, precio, size):
                        logger.log_trade(symbol, "BUY", precio, size, 0)
                        print(f"🟢 Compra {symbol}")

            except Exception as e:
                print(f"Error compra {symbol}: {e}")

        # =========================
        # 7. ESTADO DEL PORTAFOLIO
        # =========================
        print(f"\n💰 Capital actual: {portfolio.capital}")
        print(f"📊 Posiciones abiertas: {list(portfolio.posiciones.keys())}")
        print("⏳ Esperando próximo ciclo...\n")

        time.sleep(config.CYCLE_TIME)

    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        time.sleep(10)