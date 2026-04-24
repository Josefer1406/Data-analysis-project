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
    # COMPRA DINÁMICA INTELIGENTE
    # =========================
    def comprar(self, symbol, precio, features, score, tipo):

        # 🔴 evitar duplicados
        if symbol in self.posiciones:
            return False

        # 🔴 evitar sobrecarga
        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        # 🔴 FILTRO ANTI BASURA
        if score < 0.55:
            return False

        capital_disp = self.capital_disponible()

        # 🔥 ASIGNACIÓN PROGRESIVA (más capital a mejores trades)
        if score > 0.80:
            inversion = capital_disp * 0.20
        elif score > 0.72:
            inversion = capital_disp * 0.15
        elif score > 0.65:
            inversion = capital_disp * 0.11
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
    # GESTIÓN AVANZADA (TP + SL REAL)
    # =========================
    def actualizar(self, precios):

        for s in list(self.posiciones.keys()):

            if s not in precios:
                continue

            pos = self.posiciones[s]
            precio = precios[s]

            pnl = (precio - pos["entry"]) / pos["entry"]

            # actualizar máximo alcanzado
            if precio > pos["max_price"]:
                pos["max_price"] = precio

            # =========================
            # 🔻 STOP LOSS (duro)
            # =========================
            if pnl <= -0.01:
                self.cerrar(s, precio, pnl)
                continue

            # =========================
            # 🔥 NO VENDER EN RUIDO
            # =========================
            if pnl < 0.005:
                continue

            # =========================
            # 🔥 TRAILING DINÁMICO POR ETAPAS
            # =========================
            if pnl < 0.02:
                trailing_pct = 0.015   # deja respirar
            elif pnl < 0.05:
                trailing_pct = 0.02
            elif pnl < 0.10:
                trailing_pct = 0.03
            else:
                trailing_pct = 0.04   # tendencia fuerte

            trailing_price = pos["max_price"] * (1 - trailing_pct)

            # =========================
            # 🔥 TAKE PROFIT INTELIGENTE
            # =========================
            if precio < trailing_price:
                self.cerrar(s, precio, pnl)

    # =========================
    # CIERRE
    # =========================
    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones.pop(symbol)

        valor = pos["cantidad"] * precio
        self.capital += valor

        # IA aprende del resultado
        ml_model.add_sample(pos["features"], pnl)

        self.historial.append({
            "symbol": symbol,
            "entry": pos["entry"],
            "exit": precio,
            "pnl": pnl,
            "tipo": pos["tipo"]
        })

        print(f"🔴 SELL {symbol} pnl {round(pnl,4)}")

    # =========================
    # PEOR POSICIÓN
    # =========================
    def peor_posicion(self):

        peor_symbol = None
        peor_score = 999

        for s, pos in self.posiciones.items():
            if pos["score"] < peor_score:
                peor_score = pos["score"]
                peor_symbol = s

        return peor_symbol, peor_score

    # =========================
    # DATA DASHBOARD
    # =========================
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