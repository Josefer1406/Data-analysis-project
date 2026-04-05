import config
import json
import os

# =========================
# ARCHIVO DE ESTADO
# =========================
STATE_FILE = "portfolio_state.json"

# =========================
# VARIABLES
# =========================
capital = float(config.CAPITAL_INICIAL)
posiciones = {}

STOP_LOSS = -0.02
TAKE_PROFIT = 0.05


# =========================
# GUARDAR ESTADO
# =========================
def guardar_estado():
    data = {
        "capital": capital,
        "posiciones": posiciones
    }

    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


# =========================
# CARGAR ESTADO
# =========================
def cargar_estado():
    global capital, posiciones

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                capital = data.get("capital", capital)
                posiciones = data.get("posiciones", {})
                print("✅ Estado cargado correctamente")
        except Exception as e:
            print("⚠️ Error cargando estado:", e)
    else:
        print("🆕 Iniciando nuevo portfolio")


# =========================
# ABRIR POSICIÓN
# =========================
def abrir_posicion(symbol, precio, size):
    global capital

    if symbol in posiciones:
        return False

    if len(posiciones) >= config.MAX_POSICIONES:
        return False

    costo = precio * size

    if costo > capital:
        return False

    capital -= costo

    posiciones[symbol] = {
        "precio": precio,
        "size": size
    }

    guardar_estado()  # 🔥 CLAVE

    return True


# =========================
# CERRAR POSICIÓN
# =========================
def cerrar_posicion(symbol, precio):
    global capital

    pos = posiciones[symbol]

    pnl = (precio - pos["precio"]) * pos["size"]

    capital += pos["size"] * precio

    del posiciones[symbol]

    guardar_estado()  # 🔥 CLAVE

    return pnl


# =========================
# EVALUAR SALIDA
# =========================
def evaluar_salida(symbol, precio):
    pos = posiciones[symbol]

    pnl = (precio - pos["precio"]) / pos["precio"]

    return pnl <= STOP_LOSS or pnl >= TAKE_PROFIT