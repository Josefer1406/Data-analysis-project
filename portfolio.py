import time
import config
from ia_model import registrar_trade


class Portfolio:

    def __init__(self):
        self.capital = config.CAPITAL_INICIAL
        self.capital_inicial = config.CAPITAL_INICIAL

        self.posiciones = {}
        self.historial = []

        self.win = 0
        self.loss = 0

        self.cooldowns = {}

    def capital_disponible(self):
        return self.capital * (1 - config.RESERVA_CAPITAL)

    def comprar(self, symbol, precio, prob, tipo):

        if symbol in self.cooldowns:
            if time.time() < self.cooldowns[symbol]:
                return False

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        capital_disp = self.capital_disponible()

        if tipo == "elite":
            inversion = capital_disp * config.RIESGO_ELITE
        else:
            inversion = capital_disp * config.RIESGO_NORMAL

        if inversion <= 10 or inversion > self.capital:
            return False

        cantidad = inversion / precio
        self.capital -= inversion

        self.posiciones[symbol] = {
            "entry": precio,
            "cantidad": cantidad,
            "inversion": inversion,
            "prob": prob,
            "tipo": tipo,
            "time": time.time(),
            "max_price": precio
        }

        print(f"🟢 BUY {symbol} ${round(inversion,2)}")

        return True

    def actualizar(self, precios):

        for s in list(self.posiciones.keys()):

            if s not in precios:
                continue

            pos = self.posiciones[s]
            precio = precios[s]

            pnl = (precio - pos["entry"]) / pos["entry"]

            if precio > pos["max_price"]:
                pos["max_price"] = precio

            trailing = pos["max_price"] * 0.985

            if pnl > 0.012:
                self.cerrar(s, precio, pnl)

            elif pnl < -0.015:
                self.cerrar(s, precio, pnl)

            elif precio < trailing:
                self.cerrar(s, precio, pnl)

    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones.pop(symbol)

        valor = pos["cantidad"] * precio
        self.capital += valor

        if pnl > 0:
            self.win += 1
        else:
            self.loss += 1

        registrar_trade({
            "prob": pos["prob"],
            "tipo": pos["tipo"]
        }, pnl)

        self.historial.append({
            "symbol": symbol,
            "entry": pos["entry"],
            "exit": precio,
            "pnl": pnl,
            "tipo": pos["tipo"]
        })

        self.cooldowns[symbol] = time.time() + config.COOLDOWN_SYMBOL

        print(f"🔴 SELL {symbol} pnl {round(pnl,4)}")

    def peor_posicion(self):

        peor_symbol = None
        peor_prob = 999

        for s, pos in self.posiciones.items():
            if pos["prob"] < peor_prob:
                peor_prob = pos["prob"]
                peor_symbol = s

        return peor_symbol, peor_prob

    def data(self):

        pnl_total = self.capital - self.capital_inicial

        return {
            "capital": round(self.capital, 2),
            "capital_inicial": self.capital_inicial,
            "pnl": round(pnl_total, 2),
            "pnl_pct": round((pnl_total / self.capital_inicial) * 100, 2),
            "posiciones": self.posiciones,
            "historial": self.historial[-200:],
            "win": self.win,
            "loss": self.loss
        }


portfolio = Portfolio()