import config
import time

class Portfolio:

    def __init__(self):
        self.capital_total = config.CAPITAL_INICIAL
        self.capital = config.CAPITAL_INICIAL * config.USO_CAPITAL
        self.posiciones = {}
        self.historial = []
        self.last_trade = 0
        self.peak = self.capital

        print(f"🚀 Capital inicial: {self.capital_total}")

    # =========================
    # COOLDOWN DINÁMICO
    # =========================
    def cooldown(self, volatilidad):

        if volatilidad > 0.04:
            return config.COOLDOWN_BASE * 2

        elif volatilidad < 0.015:
            return config.COOLDOWN_BASE * 0.7

        return config.COOLDOWN_BASE

    def puede_operar(self, volatilidad):
        return (time.time() - self.last_trade) > self.cooldown(volatilidad)

    # =========================
    # COMPRA
    # =========================
    def comprar(self, symbol, precio, prob, volatilidad):

        if not self.puede_operar(volatilidad):
            return False

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        # sizing institucional
        if prob >= config.UMBRAL_EXCELENTE:
            size = config.SIZE_EXCELENTE
            tipo = "excelente"

        elif prob >= config.UMBRAL_BUENO:
            size = config.SIZE_BUENO_MIN
            tipo = "bueno"

        else:
            return False

        capital_trade = self.capital * size

        if capital_trade < config.MIN_TRADE_USD:
            return False

        cantidad = capital_trade / precio
        self.capital -= capital_trade

        self.posiciones[symbol] = {
            "entry": precio,
            "cantidad": cantidad,
            "inversion": capital_trade,
            "max_precio": precio,
            "tipo": tipo,
            "prob": prob,
            "vol": volatilidad,
            "trailing": False
        }

        self.last_trade = time.time()

        print(f"🟢 BUY {symbol} | ${capital_trade:.2f} | prob {prob:.2f}")

        return True

    # =========================
    # SALIDA INTELIGENTE
    # =========================
    def evaluar(self, symbol, precio):

        pos = self.posiciones[symbol]

        pnl = (precio - pos["entry"]) / pos["entry"]

        if precio > pos["max_precio"]:
            pos["max_precio"] = precio

        # activar trailing
        if pnl > config.TRAILING_START:
            pos["trailing"] = True

        # trailing adaptativo
        gap = config.TRAILING_GAP_BASE + pos["vol"]

        if pos["trailing"]:
            stop = pos["max_precio"] * (1 - gap)

            if precio <= stop:
                return True

        # stop loss
        if pnl <= config.STOP_LOSS:
            return True

        return False

    def cerrar(self, symbol, precio):

        pos = self.posiciones[symbol]

        valor = pos["cantidad"] * precio
        pnl = (precio - pos["entry"]) / pos["entry"]

        self.capital += valor

        self.historial.append({
            "symbol": symbol,
            "tipo": "SELL",
            "pnl": pnl,
            "capital": self.capital
        })

        print(f"🔴 SELL {symbol} | pnl {pnl:.4f}")

        del self.posiciones[symbol]

    def data(self):

        return {
            "capital": self.capital,
            "capital_inicial": self.capital_total,
            "posiciones": self.posiciones,
            "historial": self.historial
        }