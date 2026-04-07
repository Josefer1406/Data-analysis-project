from flask import Flask, jsonify
import threading
import time
import random

app = Flask(__name__)

# =========================
# CONFIG INSTITUCIONAL
# =========================
CAPITAL_INICIAL = 1000.0
MAX_POSICIONES = 5
MIN_HOLD_CICLOS = 3
COOLDOWN_CICLOS = 2

# position sizing institucional
SIZE_NORMAL = 0.15
SIZE_BUENA = 0.20
SIZE_EXCELENTE = 0.30

# =========================
# ESTADO GLOBAL
# =========================
capital = CAPITAL_INICIAL
posiciones = {}
historial = []

# control institucional
ultimo_trade = {}
hold_ciclos = {}

# =========================
# PRICE ENGINE (REALISTA)
# =========================
precios = {
    "BTC/USDT": 70000,
    "ETH/USDT": 2000,
    "SOL/USDT": 80,
    "XRP/USDT": 0.5,
    "ADA/USDT": 0.4,
    "DOGE/USDT": 0.1,
    "AVAX/USDT": 35,
    "LINK/USDT": 15,
    "LTC/USDT": 80,
    "ATOM/USDT": 10
}

def actualizar_precio(symbol):
    drift = 0.0005
    vol = 0.01
    cambio = drift + random.uniform(-vol, vol)
    precios[symbol] *= (1 + cambio)
    return precios[symbol]

# =========================
# SIGNAL ENGINE
# =========================
def analizar_mercado():
    señales = []

    for symbol in precios:
        precio = actualizar_precio(symbol)

        score = random.randint(0, 3)
        prob = score / 3

        print(f"{symbol} | score: {score} | prob: {prob}")

        if score >= 1:
            señales.append({
                "symbol": symbol,
                "score": score,
                "prob": prob,
                "precio": precio
            })

    return señales

# =========================
# POSITION SIZING PRO
# =========================
def calcular_size(conviccion):
    if conviccion >= 0.8:
        return SIZE_EXCELENTE
    elif conviccion >= 0.6:
        return SIZE_BUENA
    else:
        return SIZE_NORMAL

# =========================
# EXECUTION ENGINE PRO
# =========================
def ejecutar_operaciones(señales):
    global capital, posiciones

    # ordenar por mejor oportunidad
    señales = sorted(señales, key=lambda x: x["prob"], reverse=True)

    for s in señales:
        symbol = s["symbol"]
        prob = s["prob"]
        precio = s["precio"]

        # evitar sobre exposición
        if len(posiciones) >= MAX_POSICIONES:
            break

        # evitar repetir trade inmediato
        if symbol in ultimo_trade and ultimo_trade[symbol] < COOLDOWN_CICLOS:
            continue

        # evitar duplicados
        if symbol in posiciones:
            continue

        size = calcular_size(prob)
        inversion = capital * size

        if inversion <= 0:
            continue

        posiciones[symbol] = {
            "precio_entrada": precio,
            "capital": inversion,
            "ciclos": 0
        }

        capital -= inversion
        ultimo_trade[symbol] = 0
        hold_ciclos[symbol] = 0

        print(f"🟢 BUY {symbol} | convicción: {prob:.2f}")

# =========================
# RISK ENGINE (VENTAS PRO)
# =========================
def gestionar_posiciones():
    global capital, posiciones

    eliminar = []

    for symbol, pos in posiciones.items():
        precio_actual = actualizar_precio(symbol)
        pnl = (precio_actual - pos["precio_entrada"]) / pos["precio_entrada"]

        pos["ciclos"] += 1
        hold_ciclos[symbol] += 1

        print(f"🔍 {symbol} pnl: {round(pnl,4)}")

        # NO vender antes del holding mínimo
        if pos["ciclos"] < MIN_HOLD_CICLOS:
            continue

        # STOP LOSS
        if pnl < -0.02:
            print(f"🔴 STOP LOSS {symbol}")
            capital += pos["capital"] * (1 + pnl)
            eliminar.append(symbol)

        # TAKE PROFIT dinámico
        elif pnl > 0.03:
            print(f"💰 TAKE PROFIT {symbol}")
            capital += pos["capital"] * (1 + pnl)
            eliminar.append(symbol)

    for s in eliminar:
        posiciones.pop(s, None)
        hold_ciclos.pop(s, None)

# =========================
# LOOP PRINCIPAL
# =========================
def run_bot():
    global ultimo_trade

    while True:
        print("\n🔎 Analizando mercado...")

        señales = analizar_mercado()
        gestionar_posiciones()
        ejecutar_operaciones(señales)

        # actualizar cooldowns
        for s in ultimo_trade:
            ultimo_trade[s] += 1

        print(f"💰 Capital: {capital}")
        print(f"📊 Posiciones: {list(posiciones.keys())}")
        print("⏳ Ciclo completado...\n")

        time.sleep(10)

# =========================
# API
# =========================
@app.route("/data")
def data():
    return jsonify({
        "capital": capital,
        "posiciones": posiciones
    })

@app.route("/reset")
def reset():
    global capital, posiciones, historial, ultimo_trade, hold_ciclos

    capital = CAPITAL_INICIAL
    posiciones = {}
    historial = []
    ultimo_trade = {}
    hold_ciclos = {}

    print("🧹 Base reiniciada")
    print("🔄 Capital restaurado a 1000")

    return jsonify({"status": "reset ok"})

# =========================
# START
# =========================
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)