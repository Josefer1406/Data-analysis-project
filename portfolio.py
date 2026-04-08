import config
import time
import csv
import os

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
    # EXPOSICIÓN REAL
    # =========================
    def capital_invertido(self):
        return sum(p["inversion"] for p in self.posiciones.values())

    def exposicion_actual(self):
        return self.capital_invertido() / self.capital_inicial

    # =========================
    # COOLDOWN DINÁMICO
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
    # FILTRO ANTICORRELACIÓN
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
    # COMPRA INSTITUCIONAL
    # =========================
    def comprar(self, symbol, precio, prob):

        if not self.puede_operar():
            return False

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        if self.correlacionado(symbol):
            print(f"⛔ Correlación evitada: {symbol}")
            return False

        # SIZE POR CONVICCIÓN
        if prob >= 0.9:
            size = 0.30
        elif prob >= 0.75:
            size = 0.18
        else:
            return False

        capital_trade = self.capital_inicial * size

        # CONTROL GLOBAL
        if (self.capital_invertido() + capital_trade) > (self.capital_inicial * config.USO_CAPITAL):
            print(f"⛔ Límite capital alcanzado")
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
    # GESTIÓN DE POSICIONES
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

            # trailing activation
            if pnl > config.TRAILING_START:
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
    # CIERRE DE POSICIÓN
    # =========================
    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones[symbol]

        valor = pos["cantidad"] * precio
        self.capital += valor

        trade = {
            "symbol": symbol,
            "pnl": float(round(pnl, 4)),
            "capital": float(round(self.capital, 2)),
            "tipo": "SELL",
            "timestamp": time.time()
        }

        self.historial.append(trade)

        print(f"🔴 SELL {symbol} | pnl {pnl:.4f}")

        del self.posiciones[symbol]

    # =========================
    # PERFORMANCE
    # =========================
    def resumen_performance(self):

        total_trades = len(self.historial)

        if total_trades == 0:
            winrate = 0
        else:
            wins = sum(1 for t in self.historial if t["pnl"] > 0)
            winrate = round(wins / total_trades, 2)

        capital_final = round(self.capital, 2)
        pnl = round(capital_final - self.capital_inicial, 2)

        if self.capital_inicial > 0:
            pnl_pct = round((pnl / self.capital_inicial) * 100, 2)
        else:
            pnl_pct = 0

        return {
            "timestamp": time.time(),
            "version": getattr(config, "BOT_VERSION", "v1"),
            "capital_inicial": self.capital_inicial,
            "capital_final": capital_final,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "trades": total_trades,
            "winrate": winrate,
            "posiciones": len(self.posiciones)
        }

    # =========================
    # GUARDAR RESULTADOS (PRO)
    # =========================
    def guardar_resultados(self):

        archivo = "resultados_bot.csv"
        data = self.resumen_performance()

        existe = os.path.isfile(archivo)

        with open(archivo, mode="a", newline="") as f:

            writer = csv.DictWriter(f, fieldnames=data.keys())

            if not existe:
                writer.writeheader()

            writer.writerow(data)

    # =========================
    # DATA STREAMLIT
    # =========================
    def data(self):

        capital_actual = round(self.capital, 2)
        capital_inicial = self.capital_inicial

        pnl = round(capital_actual - capital_inicial, 2)

        if capital_inicial > 0:
            pnl_pct = round((pnl / capital_inicial) * 100, 2)
        else:
            pnl_pct = 0

        return {
            "capital": capital_actual,
            "capital_inicial": capital_inicial,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "posiciones": self.posiciones,
            "historial": self.historial
        }


portfolio = Portfolio()