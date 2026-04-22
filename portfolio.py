import time
import config
from ml_v3.model import ml_model


class Portfolio:

    def __init__(self):
        self.capital = config.CAPITAL_INICIAL
        self.capital_inicial = config.CAPITAL_INICIAL

        self.posiciones = {}
        self.historial = []

    def capital_disponible(self):
        return self.capital * (1 - config.RESERVA_CAPITAL)

    # =========================
    # COMPRA DINÁMICA
    # =========================
    def comprar(self, symbol, precio, features, score, tipo):

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        capital_disp = self.capital_disponible()

        # 🔥 ASIGNACIÓN INTELIGENTE
        if score > 0.75:
            inversion = capital_disp * 0.18
        elif score > 0.65:
            inversion = capital_disp * 0.12
        else:
            inversion = capital_disp * 0.08

        if inversion <= 10 or inversion > self.capital:
            return False

        cantidad = inversion / precio
        self.capital -= inversion

        self.posiciones[symbol] = {
            "entry": precio,
            "cantidad": cantidad,
            "inversion": inversion,
            "features": features,
            "score": score,
            "tipo": tipo,
            "time": time.time(),
            "max_price": precio
        }

        print(f"🟢 BUY {symbol} ${round(inversion,2)} score {round(score,2)}")

        return True

    # =========================
    # GESTIÓN (TP + SL REAL)
    # =========================
    def actualizar(self, precios):

        for s in list(self.posiciones.keys()):

            if s not in precios:
                continue

            pos = self.posiciones[s]
            precio = precios[s]

            pnl = (precio - pos["entry"]) / pos["entry"]

            # actualizar máximo
            if precio > pos["max_price"]:
                pos["max_price"] = precio

            # =========================
            # 🔥 TRAILING PROFIT
            # =========================
            trailing_pct = 0.01  # 1% caída desde el máximo

            trailing_price = pos["max_price"] * (1 - trailing_pct)

            # =========================
            # 🔻 STOP LOSS
            # =========================
            if pnl <= -0.01:
                self.cerrar(s, precio, pnl)
                continue

            # =========================
            # 🔥 TAKE PROFIT INTELIGENTE
            # =========================
            if precio < trailing_price and pnl > 0:
                self.cerrar(s, precio, pnl)

    # =========================
    # CIERRE
    # =========================
    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones.pop(symbol)

        valor = pos["cantidad"] * precio
        self.capital += valor

        # IA aprende
        ml_model.add_sample(pos["features"], pnl)

        self.historial.append({
            "symbol": symbol,
            "entry": pos["entry"],
            "exit": precio,
            "pnl": pnl,
            "tipo": pos["tipo"]
        })

        print(f"🔴 SELL {symbol} pnl {round(pnl,4)}")

    def peor_posicion(self):

        peor_symbol = None
        peor_score = 999

        for s, pos in self.posiciones.items():
            if pos["score"] < peor_score:
                peor_score = pos["score"]
                peor_symbol = s

        return peor_symbol, peor_score

    def data(self):

        pnl_total = self.capital - self.capital_inicial

        return {
            "capital": round(self.capital, 2),
            "capital_inicial": self.capital_inicial,
            "pnl": round(pnl_total, 2),
            "pnl_pct": round((pnl_total / self.capital_inicial) * 100, 2),
            "posiciones": self.posiciones,
            "historial": self.historial[-200:]
        }


portfolio = Portfolio()