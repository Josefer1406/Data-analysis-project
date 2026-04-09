import config
import time
import csv

class Portfolio:

    def __init__(self):
        self.capital_inicial = config.CAPITAL_INICIAL
        self.capital = config.CAPITAL_INICIAL
        self.posiciones = {}
        self.historial = []
        self.last_trade = 0
        self.cooldown = config.COOLDOWN_BASE

        print(f"🚀 Capital inicial: {self.capital_inicial}")

    # =========================
    # EXPOSICIÓN
    # =========================
    def capital_invertido(self):
        return sum(p["inversion"] for p in self.posiciones.values())

    def exposicion_actual(self):
        return self.capital_invertido() / self.capital_inicial

    # =========================
    # COOLDOWN
    # =========================
    def actualizar_cooldown(self):

        if len(self.historial) < 5:
            self.cooldown = 15
            return

        ultimos = self.historial[-5:]
        winrate = sum(1 for t in ultimos if t["pnl"] > 0) / len(ultimos)

        if winrate < 0.4:
            self.cooldown = 60
        elif winrate > 0.7:
            self.cooldown = 10
        else:
            self.cooldown = 25

    def puede_operar(self):
        return (time.time() - self.last_trade) > self.cooldown

    # =========================
    # ANTICORRELACIÓN
    # =========================
    def correlacionado(self, symbol):

        grupo_nuevo = None
        for g, lista in config.CORRELACION.items():
            if symbol in lista:
                grupo_nuevo = g

        for s in self.posiciones:
            for g, lista in config.CORRELACION.items():
                if s in lista and g == grupo_nuevo:
                    return True

        return False

    # =========================
    # PEOR POSICIÓN (🔥 NUEVO)
    # =========================
    def peor_posicion(self, precios):

        peor_symbol = None
        peor_score = 999

        for symbol, pos in self.posiciones.items():

            precio = precios.get(symbol)
            if precio is None:
                continue

            pnl = (precio - pos["entry"]) / pos["entry"]

            # score negativo → peor
            score = pnl

            if score < peor_score:
                peor_score = score
                peor_symbol = symbol

        return peor_symbol, peor_score

    # =========================
    # COMPRA CON ROTACIÓN
    # =========================
    def comprar(self, symbol, precio, prob, score_nuevo=None, precios=None):

        if not self.puede_operar():
            return False

        if symbol in self.posiciones:
            return False

        # =========================
        # ROTACIÓN SI ESTÁ LLENO
        # =========================
        if len(self.posiciones) >= config.MAX_POSICIONES:

            if precios is None or score_nuevo is None:
                return False

            peor_symbol, peor_score = self.peor_posicion(precios)

            # 🔥 solo rotar si el nuevo es mejor
            if peor_score >= 0:
                return False

            if prob < 0.80:
                return False

            print(f"🔁 ROTANDO: sale {peor_symbol} → entra {symbol}")

            self.cerrar(peor_symbol, precios[peor_symbol], peor_score)

        # =========================
        # FILTROS
        # =========================
        if self.correlacionado(symbol):
            print(f"⛔ Correlación evitada: {symbol}")
            return False

        # SIZE
        if prob >= 0.9:
            size = 0.25
        elif prob >= 0.75:
            size = 0.15
        else:
            return False

        capital_trade = self.capital_inicial * size

        if (self.capital_invertido() + capital_trade) > (self.capital_inicial * config.USO_CAPITAL):
            return False

        if capital_trade > self.capital:
            return False

        cantidad = capital_trade / precio
        self.capital -= capital_trade

        self.posiciones[symbol] = {
            "entry": precio,
            "cantidad": cantidad,
            "inversion": capital_trade,
            "max_precio": precio,
            "prob": prob,
            "trailing": False,
            "break_even": False,
            "tiempo": time.time()
        }

        self.last_trade = time.time()

        print(f"🟢 BUY {symbol} | ${capital_trade:.2f} | prob {prob:.2f}")

        return True

    # =========================
    # GESTIÓN
    # =========================
    def actualizar(self, precios):

        for symbol in list(self.posiciones.keys()):

            pos = self.posiciones[symbol]
            precio = precios.get(symbol)

            if precio is None:
                continue

            pnl = (precio - pos["entry"]) / pos["entry"]

            if precio > pos["max_precio"]:
                pos["max_precio"] = precio

            # salida temprana
            if pnl < -0.01:
                self.cerrar(symbol, precio, pnl)
                continue

            # break even
            if pnl > 0.015:
                pos["break_even"] = True

            if pos["break_even"] and pnl <= 0:
                self.cerrar(symbol, precio, pnl)
                continue

            # trailing
            if pnl > config.TRAILING_START:
                pos["trailing"] = True

            if pos["trailing"]:
                gap = config.TRAILING_GAP

                if pnl > 0.05:
                    gap = 0.01

                stop = pos["max_precio"] * (1 - gap)

                if precio <= stop:
                    self.cerrar(symbol, precio, pnl)
                    continue

            # stop duro
            if pnl <= config.STOP_LOSS:
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
            "pnl": float(round(pnl, 4)),
            "capital": float(round(self.capital, 2)),
            "tipo": "SELL"
        }

        self.historial.append(trade)

        print(f"🔴 SELL {symbol} | pnl {pnl:.4f}")

        del self.posiciones[symbol]

    # =========================
    # DATA
    # =========================
    def data(self):

        capital_actual = round(self.capital, 2)
        pnl = round(capital_actual - self.capital_inicial, 2)
        pnl_pct = round((pnl / self.capital_inicial) * 100, 2)

        return {
            "capital": capital_actual,
            "capital_inicial": self.capital_inicial,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "posiciones": self.posiciones,
            "historial": self.historial
        }


portfolio = Portfolio()