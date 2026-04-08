import config
import time
import random

class Portfolio:

    def __init__(self):
        self.capital_total = config.CAPITAL_INICIAL
        self.capital = config.CAPITAL_INICIAL * config.USO_CAPITAL
        self.posiciones = {}
        self.historial = []
        self.last_trade = 0

        print("🚀 BOT INSTITUCIONAL INICIADO")

    def grupo(self, symbol):
        for g, lista in config.CORRELACION.items():
            if symbol in lista:
                return g
        return None

    def correlacion(self, symbol):
        g = self.grupo(symbol)
        for s in self.posiciones:
            if self.grupo(s) == g:
                return True
        return False

    def puede_operar(self):
        return (time.time() - self.last_trade) > config.COOLDOWN

    def comprar(self, symbol, precio, prob):

        if not self.puede_operar():
            return

        if symbol in self.posiciones:
            return

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return

        if self.correlacion(symbol):
            return

        if prob >= config.UMBRAL_EXCELENTE:
            size = config.SIZE_EXCELENTE
            tipo = "excelente"

        elif prob >= config.UMBRAL_BUENO:
            size = random.uniform(config.SIZE_BUENO_MIN, config.SIZE_BUENO_MAX)
            tipo = "bueno"

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
            "tipo": tipo,
            "prob": float(prob),
            "trailing": False
        }

        self.last_trade = time.time()

        print(f"🟢 BUY {symbol} | ${capital_trade:.2f} | {tipo} | prob: {prob:.2f}")

    def evaluar(self, precios):

        for symbol in list(self.posiciones.keys()):

            pos = self.posiciones[symbol]
            precio = precios[symbol]

            pnl = (precio - pos["precio"]) / pos["precio"]

            if precio > pos["max_precio"]:
                pos["max_precio"] = precio

            if pnl > config.TRAILING_START:
                pos["trailing"] = True

            if pnl <= config.STOP_LOSS:
                self.cerrar(symbol, precio, pnl)
                continue

            if pos["trailing"]:
                stop = pos["max_precio"] * (1 - config.TRAILING_GAP)
                if precio <= stop:
                    self.cerrar(symbol, precio, pnl)

    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones[symbol]

        valor = pos["cantidad"] * precio
        self.capital += valor

        trade = {
            "symbol": symbol,
            "tipo": pos["tipo"],
            "prob": float(pos["prob"]),
            "pnl": float(round(pnl, 4)),
            "capital": float(round(self.capital, 2))
        }

        self.historial.append(trade)

        print(f"💰 SELL {symbol} | pnl: {pnl:.4f}")

        del self.posiciones[symbol]

    # 🔥 DATA COMPLETA PARA STREAMLIT
    def data(self):

        return {
            "capital": round(self.capital, 2),

            "posiciones": self.posiciones,  # 🔥 AHORA COMPLETO

            "num_posiciones": len(self.posiciones),

            "trades": len(self.historial),

            "historial": self.historial[-20:]
        }