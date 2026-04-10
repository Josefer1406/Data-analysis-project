import config
import time

class Portfolio:

    def __init__(self):
        self.capital_inicial = config.CAPITAL_INICIAL
        self.capital = config.CAPITAL_INICIAL
        self.posiciones = {}
        self.historial = []
        self.last_trade = 0
        self.cooldown = config.COOLDOWN_BASE

        print(f"🚀 Capital inicial: {self.capital_inicial}")

    def puede_operar(self):
        return (time.time() - self.last_trade) > self.cooldown

    def capital_invertido(self):
        return sum(p["inversion"] for p in self.posiciones.values())

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

    def comprar(self, symbol, precio, prob):

        if not self.puede_operar():
            return False

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        if self.correlacionado(symbol):
            return False

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

    def actualizar(self, precios):

        for symbol in list(self.posiciones.keys()):

            pos = self.posiciones[symbol]
            precio = precios.get(symbol)

            if precio is None:
                continue

            pnl = (precio - pos["entry"]) / pos["entry"]

            # actualizar max
            if precio > pos["max_precio"]:
                pos["max_precio"] = precio

            # activar trailing
            if pnl > config.TRAILING_START:
                pos["trailing"] = True

            # stop loss
            if pnl <= config.STOP_LOSS:
                print(f"🛑 STOP LOSS {symbol}")
                self.cerrar(symbol, precio, pnl)
                continue

            # trailing
            if pos["trailing"]:
                stop = pos["max_precio"] * (1 - config.TRAILING_GAP)
                if precio <= stop:
                    print(f"📉 TRAILING {symbol}")
                    self.cerrar(symbol, precio, pnl)
                    continue

            # 🔥 SALIDA POR TIEMPO
            tiempo_max = 60 * 60 * 2  # 2 horas

            if time.time() - pos["timestamp"] > tiempo_max:
                print(f"⏰ CIERRE POR TIEMPO {symbol}")
                self.cerrar(symbol, precio, pnl)
                continue

    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones[symbol]

        valor = pos["cantidad"] * precio
        self.capital += valor

        self.historial.append({
            "symbol": symbol,
            "pnl": round(pnl, 4),
            "capital": round(self.capital, 2),
            "tipo": "SELL"
        })

        print(f"🔴 SELL {symbol} | pnl {pnl:.4f}")

        del self.posiciones[symbol]

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

    def data(self):
        return {
            "capital": round(self.capital, 2),
            "capital_inicial": self.capital_inicial,
            "posiciones": self.posiciones,
            "historial": self.historial
        }


portfolio = Portfolio()