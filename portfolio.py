import config
import random
import time

class Portfolio:

    def __init__(self):
        self.capital_total = config.CAPITAL_INICIAL
        self.capital = config.CAPITAL_INICIAL * config.USO_CAPITAL
        self.posiciones = {}
        self.historial = []
        self.last_trade_time = 0

        print(f"🚀 Capital inicial: {self.capital_total}")

    # =========================
    # CORRELACIÓN
    # =========================

    def grupo(self, symbol):
        for g, activos in config.CORRELACION_GRUPOS.items():
            if symbol in activos:
                return g
        return None

    def correlacion(self, symbol):
        g = self.grupo(symbol)
        for s in self.posiciones:
            if self.grupo(s) == g:
                return True
        return False

    # =========================
    # COOLDOWN DINÁMICO
    # =========================

    def puede_operar(self):
        ahora = time.time()
        return (ahora - self.last_trade_time) > config.COOLDOWN_BASE

    # =========================
    # COMPRA INSTITUCIONAL
    # =========================

    def comprar(self, symbol, precio, prob):

        if not self.puede_operar():
            return

        if symbol in self.posiciones:
            return

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return

        if self.correlacion(symbol):
            return

        # calidad de señal
        if prob >= config.UMBRAL_EXCELENTE:
            size = config.SIZE_EXCELENTE

        elif prob >= config.UMBRAL_BUENO:
            size = random.uniform(config.SIZE_BUENO_MIN, config.SIZE_BUENO_MAX)

        else:
            return

        capital_trade = self.capital * size

        if capital_trade < config.MIN_TRADE_USD:
            return

        cantidad = capital_trade / precio

        self.capital -= capital_trade

        self.posiciones[symbol] = {
            "precio": precio,
            "cantidad": cantidad,
            "inversion": capital_trade,
            "max_precio": precio,
            "trailing": False
        }

        self.last_trade_time = time.time()

        print(f"🟢 BUY {symbol} | ${capital_trade:.2f} | prob: {prob:.2f}")

    # =========================
    # GESTIÓN DINÁMICA
    # =========================

    def evaluar(self, precios):

        for symbol in list(self.posiciones.keys()):

            if symbol not in precios:
                continue

            pos = self.posiciones[symbol]

            precio = precios[symbol]
            pnl = (precio - pos["precio"]) / pos["precio"]

            # actualizar máximo
            if precio > pos["max_precio"]:
                pos["max_precio"] = precio

            # activar trailing
            if pnl >= config.TRAILING_START:
                pos["trailing"] = True

            # stop loss
            if pnl <= config.STOP_LOSS:
                self.cerrar(symbol, precio, pnl)
                continue

            # trailing dinámico
            if pos["trailing"]:
                stop = pos["max_precio"] * (1 - config.TRAILING_GAP)

                if precio <= stop:
                    self.cerrar(symbol, precio, pnl)

    # =========================
    # CIERRE
    # =========================

    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones[symbol]

        valor = pos["cantidad"] * precio
        self.capital += valor

        trade = {
            "symbol": symbol,
            "pnl": round(pnl, 4),
            "capital": round(self.capital, 2)
        }

        self.historial.append(trade)

        print(f"💰 SELL {symbol} | pnl: {pnl:.4f} | capital: {self.capital:.2f}")

        del self.posiciones[symbol]

    # =========================
    # DATA LIMPIA STREAMLIT
    # =========================

    def data(self):

        return {
            "capital": float(round(self.capital, 2)),
            "capital_total": float(self.capital_total),
            "num_posiciones": int(len(self.posiciones)),
            "posiciones": list(self.posiciones.keys()),
            "trades": int(len(self.historial)),
            "historial": list(self.historial)
        }