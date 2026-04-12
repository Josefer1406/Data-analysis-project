import config
import time


class Portfolio:

    def __init__(self):
        self.capital = config.CAPITAL_INICIAL
        self.capital_inicial = config.CAPITAL_INICIAL
        self.posiciones = {}
        self.historial = []

    def comprar(self, symbol, precio, prob, inversion):

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        if inversion > self.capital:
            return False

        cantidad = inversion / precio

        self.capital -= inversion

        self.posiciones[symbol] = {
            "entry": precio,
            "cantidad": cantidad,
            "inversion": inversion,
            "prob": prob,
            "max_precio": precio,
            "timestamp": time.time(),
            "trailing": False
        }

        print(f"🟢 BUY {symbol} ${round(inversion,2)}")

        return True

    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones[symbol]

        valor = pos["cantidad"] * precio
        self.capital += valor

        self.historial.append({
            "symbol": symbol,
            "pnl": pnl,
            "capital": self.capital
        })

        print(f"🔴 SELL {symbol} pnl {round(pnl,4)}")

        del self.posiciones[symbol]

    def actualizar(self, precios):

        for symbol in list(self.posiciones.keys()):

            pos = self.posiciones[symbol]
            precio = precios.get(symbol)

            if precio is None:
                continue

            pnl = (precio - pos["entry"]) / pos["entry"]

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
                    continue

            # salida por tiempo
            if time.time() - pos["timestamp"] > 7200:
                self.cerrar(symbol, precio, pnl)

    def data(self):
        return {
            "capital": round(self.capital, 2),
            "posiciones": self.posiciones,
            "historial": self.historial
        }


portfolio = Portfolio()