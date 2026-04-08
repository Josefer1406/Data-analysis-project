import config
import time

class Portfolio:

    def __init__(self):
        self.capital_inicial = config.CAPITAL_INICIAL
        self.capital = config.CAPITAL_INICIAL
        self.posiciones = {}
        self.historial = []
        self.last_trade = 0

        print(f"🚀 Capital inicial: {self.capital}")

    # =========================
    # EXPOSICIÓN TOTAL
    # =========================
    def capital_invertido(self):
        return sum([p["inversion"] for p in self.posiciones.values()])

    def exposicion_actual(self):
        return self.capital_invertido() / self.capital_inicial

    # =========================
    # COOLDOWN (base)
    # =========================
    def puede_operar(self):
        return (time.time() - self.last_trade) > config.COOLDOWN_BASE

    # =========================
    # BUY (CONTROL INSTITUCIONAL)
    # =========================
    def comprar(self, symbol, precio, prob, vol):

        if not self.puede_operar():
            return False

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        # 🚨 CONTROL GLOBAL (CLAVE)
        if self.exposicion_actual() >= config.USO_CAPITAL:
            return False

        # =========================
        # SIZE POR CONVICCIÓN
        # =========================
        if prob >= 0.9:
            size = 0.30
        elif prob >= 0.75:
            size = 0.18
        else:
            return False

        capital_trade = self.capital_inicial * size

        # 🚨 evitar sobrepasar 60%
        if self.capital_invertido() + capital_trade > self.capital_inicial * config.USO_CAPITAL:
            return False

        if capital_trade < config.MIN_TRADE_USD:
            return False

        cantidad = capital_trade / precio

        self.capital -= capital_trade

        self.posiciones[symbol] = {
            "entry": precio,
            "cantidad": cantidad,
            "inversion": capital_trade,
            "max_precio": precio,
            "prob": prob,
            "trailing": False
        }

        self.last_trade = time.time()

        print(f"🟢 BUY {symbol} | ${capital_trade:.2f} | prob {prob:.2f}")

        return True

    # =========================
    # EVALUAR
    # =========================
    def evaluar(self, symbol, precio):

        if symbol not in self.posiciones:
            return False

        pos = self.posiciones[symbol]

        entry = pos["entry"]
        pnl = (precio - entry) / entry

        # actualizar máximo
        if precio > pos["max_precio"]:
            pos["max_precio"] = precio

        # activar trailing
        if pnl > config.TRAILING_START:
            pos["trailing"] = True

        # STOP LOSS
        if pnl <= config.STOP_LOSS:
            self.cerrar(symbol, precio, pnl)
            return True

        # TRAILING DINÁMICO (ligado a volatilidad)
        trailing_gap = config.TRAILING_GAP_BASE * (1 + pos["prob"])

        if pos["trailing"]:
            stop = pos["max_precio"] * (1 - trailing_gap)

            if precio <= stop:
                self.cerrar(symbol, precio, pnl)
                return True

        return False

    # =========================
    # SELL
    # =========================
    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones[symbol]

        valor = pos["cantidad"] * precio
        self.capital += valor

        self.historial.append({
            "symbol": symbol,
            "tipo": "SELL",
            "pnl": round(pnl, 4),
            "capital": round(self.capital, 2)
        })

        print(f"🔴 SELL {symbol} | pnl: {pnl:.4f}")

        del self.posiciones[symbol]

    # =========================
    # DATA STREAMLIT
    # =========================
    def data(self):

        return {
            "capital": round(self.capital, 2),
            "capital_inicial": self.capital_inicial,
            "exposicion": round(self.exposicion_actual(), 2),
            "posiciones": self.posiciones,
            "historial": self.historial[-50]
        }