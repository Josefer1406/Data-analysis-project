import config
import time
import csv
import os

class Portfolio:

    def __init__(self):
        self.capital_inicial = config.CAPITAL_INICIAL
        self.capital = config.CAPITAL_INICIAL
        self.peak_capital = self.capital

        self.posiciones = {}
        self.historial = []

        self.last_trade = 0
        self.cooldown = config.COOLDOWN_BASE

        self.modo_defensivo = False

        print(f"🚀 Capital inicial: {self.capital_inicial}")

    # =========================
    # EXPOSICIÓN
    # =========================
    def capital_invertido(self):
        return sum(p["inversion"] for p in self.posiciones.values())

    def exposicion_actual(self):
        return self.capital_invertido() / self.capital_inicial

    # =========================
    # DRAWDOWN CONTROL (🔥 CLAVE)
    # =========================
    def actualizar_drawdown(self):

        if self.capital > self.peak_capital:
            self.peak_capital = self.capital

        dd = (self.capital - self.peak_capital) / self.peak_capital

        # 🔴 CORTE TOTAL
        if dd < -0.25:
            print("🛑 STOP TOTAL: drawdown crítico")
            return False

        # 🟡 MODO DEFENSIVO
        if dd < -0.10:
            self.modo_defensivo = True
        else:
            self.modo_defensivo = False

        return True

    # =========================
    # COOLDOWN DINÁMICO
    # =========================
    def actualizar_cooldown(self):

        if len(self.historial) < 5:
            self.cooldown = 20
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
    # COMPRA INTELIGENTE
    # =========================
    def comprar(self, symbol, precio, prob):

        if not self.actualizar_drawdown():
            return False

        if not self.puede_operar():
            return False

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        if self.correlacionado(symbol):
            print(f"⛔ Correlación evitada: {symbol}")
            return False

        # 🔥 IA DE RIESGO
        if prob >= 0.9:
            size = 0.30
        elif prob >= 0.75:
            size = 0.18
        else:
            return False

        # 🔴 MODO DEFENSIVO
        if self.modo_defensivo:
            size *= 0.5  # reduce riesgo

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
            "trailing": False
        }

        self.last_trade = time.time()

        print(f"🟢 BUY {symbol} | ${capital_trade:.2f} | prob {prob:.2f}")

        return True

    # =========================
    # GESTIÓN POSICIONES
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

        self.historial.append({
            "symbol": symbol,
            "pnl": pnl,
            "capital": self.capital,
            "tipo": "SELL",
            "timestamp": time.time()
        })

        print(f"🔴 SELL {symbol} | pnl {pnl:.4f}")

        del self.posiciones[symbol]

    # =========================
    # PERFORMANCE
    # =========================
    def resumen_performance(self):

        total = len(self.historial)
        wins = sum(1 for t in self.historial if t["pnl"] > 0)

        winrate = (wins / total) if total > 0 else 0

        pnl = self.capital - self.capital_inicial

        return {
            "capital": self.capital,
            "pnl": pnl,
            "winrate": round(winrate, 2),
            "trades": total
        }

    # =========================
    # GUARDADO
    # =========================
    def guardar_resultados(self):

        archivo = "resultados_bot.csv"
        data = self.resumen_performance()

        existe = os.path.isfile(archivo)

        with open(archivo, "a", newline="") as f:

            writer = csv.DictWriter(f, fieldnames=data.keys())

            if not existe:
                writer.writeheader()

            writer.writerow(data)

    # =========================
    # DATA API
    # =========================
    def data(self):
        return {
            "capital": self.capital,
            "capital_inicial": self.capital_inicial,
            "posiciones": self.posiciones,
            "historial": self.historial,
            "modo_defensivo": self.modo_defensivo
        }


portfolio = Portfolio()