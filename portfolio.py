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
    # CORRELACIÓN
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
    # COMPRA
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

        # SIZE
        if prob >= 0.9:
            size = 0.30
        elif prob >= 0.75:
            size = 0.18
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
            "timestamp": time.time()  # 🔥 CLAVE
        }

        self.last_trade = time.time()

        print(f"🟢 BUY {symbol} | ${capital_trade:.2f}")

        return True

    # =========================
    # ACTUALIZAR (🔥 FIX REAL)
    # =========================
    def actualizar(self, precios):

        for symbol in list(self.posiciones.keys()):

            pos = self.posiciones[symbol]
            precio = precios.get(symbol)

            if precio is None:
                continue

            # 🔥 FIX: asegurar timestamp
            if "timestamp" not in pos:
                pos["timestamp"] = time.time()

            pnl = (precio - pos["entry"]) / pos["entry"]

            print(f"📊 {symbol} pnl: {round(pnl,4)}")

            # actualizar max
            if precio > pos["max_precio"]:
                pos["max_precio"] = precio

            # activar trailing
            if pnl > config.TRAILING_START:
                pos["trailing"] = True

            # =========================
            # STOP LOSS
            # =========================
            if pnl <= config.STOP_LOSS:
                print(f"🛑 STOP LOSS {symbol}")
                self.cerrar(symbol, precio, pnl)
                continue

            # =========================
            # TRAILING
            # =========================
            if pos["trailing"]:
                stop = pos["max_precio"] * (1 - config.TRAILING_GAP)
                if precio <= stop:
                    print(f"📉 TRAILING {symbol}")
                    self.cerrar(symbol, precio, pnl)
                    continue

            # =========================
            # 🔥 TIEMPO (CLAVE)
            # =========================
            tiempo_trade = time.time() - pos["timestamp"]

            print(f"⏱ {symbol} tiempo: {int(tiempo_trade)}s")

            if tiempo_trade > 7200:  # 2 horas
                print(f"⏰ CIERRE FORZADO {symbol}")
                self.cerrar(symbol, precio, pnl)
                continue

    # =========================
    # CERRAR
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
    # GUARDAR
    # =========================
    def guardar_resultados(self):

        data = {
            "capital_final": self.capital,
            "trades": len(self.historial)
        }

        with open("resultados_bot.csv", "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())

            if f.tell() == 0:
                writer.writeheader()

            writer.writerow(data)

    # =========================
    # DATA
    # =========================
    def data(self):

        capital_actual = round(self.capital, 2)
        pnl = round(capital_actual - self.capital_inicial, 2)

        return {
            "capital": capital_actual,
            "capital_inicial": self.capital_inicial,
            "pnl": pnl,
            "posiciones": self.posiciones,
            "historial": self.historial
        }


portfolio = Portfolio()