import time
import config


class Portfolio:

    def __init__(self):
        self.capital = config.CAPITAL_INICIAL
        self.posiciones = {}
        self.historial = []

        self.win = 0
        self.loss = 0

        self.cooldowns = {}

    # =========================
    # IA
    # =========================
    def ajustar_filtro(self):

        total = self.win + self.loss

        if total < 20:
            return 0.70  # 🔥 menos agresivo al inicio

        winrate = self.win / total

        if winrate < 0.4:
            return 0.72  # 🔥 antes 0.75 (muy alto)

        if winrate > 0.6:
            return 0.65

        return 0.70

    # =========================
    def actualizar(self, precios):

        for s in list(self.posiciones.keys()):

            if s not in precios:
                continue

            pos = self.posiciones[s]
            precio_actual = precios[s]

            pnl = (precio_actual - pos["entry"]) / pos["entry"]

            if pnl > 0.015:
                self.cerrar(s, precio_actual, pnl)

            elif pnl < -0.02:
                self.cerrar(s, precio_actual, pnl)

    # =========================
    def comprar(self, symbol, precio, prob, tipo):

        if symbol in self.cooldowns:
            if time.time() < self.cooldowns[symbol]:
                return False

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        capital_operable = self.capital * (1 - config.RESERVA_CAPITAL)

        if tipo == "elite":
            inversion = capital_operable * config.RIESGO_ELITE
        else:
            inversion = capital_operable * config.RIESGO_NORMAL

        if inversion <= 10 or inversion > self.capital:
            return False

        self.capital -= inversion

        self.posiciones[symbol] = {
            "entry": precio,
            "inversion": inversion,
            "prob": prob,
            "tipo": tipo,
            "time": time.time()
        }

        print(f"🟢 BUY {symbol} ${round(inversion,2)}")

        return True

    # =========================
    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones.pop(symbol)

        resultado = pos["inversion"] * (1 + pnl)
        self.capital += resultado

        # IA
        if pnl > 0:
            self.win += 1
        else:
            self.loss += 1

        # 🔥 GUARDAR HISTORIAL (CLAVE)
        self.historial.append({
            "symbol": symbol,
            "entry": pos["entry"],
            "exit": precio,
            "pnl": pnl,
            "tipo": pos["tipo"],
            "duracion": time.time() - pos["time"]
        })

        self.cooldowns[symbol] = time.time() + config.COOLDOWN_SYMBOL

        print(f"🔴 SELL {symbol} pnl {round(pnl,4)}")

    # =========================
    def data(self):
        return {
            "capital": round(self.capital, 2),
            "posiciones": self.posiciones,
            "historial": self.historial[-50:],  # últimos trades
            "win": self.win,
            "loss": self.loss
        }


portfolio = Portfolio()