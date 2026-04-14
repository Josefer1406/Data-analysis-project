import time
import config


class Portfolio:

    def __init__(self):
        self.capital = config.CAPITAL_INICIAL
        self.posiciones = {}
        self.historial = []

        # IA
        self.win = 0
        self.loss = 0

        # cooldown por símbolo
        self.cooldowns = {}

    # =========================
    # IA ADAPTATIVA
    # =========================
    def ajustar_filtro(self):

        if not config.IA_ADAPTATIVA:
            return config.PROB_MIN

        total = self.win + self.loss

        if total < 10:
            return config.PROB_MIN

        winrate = self.win / total

        if winrate < 0.4:
            return 0.75

        if winrate > 0.6:
            return 0.65

        return config.PROB_MIN

    # =========================
    # ACTUALIZAR POSICIONES
    # =========================
    def actualizar(self, precios):

        for s in list(self.posiciones.keys()):

            if s not in precios:
                continue

            pos = self.posiciones[s]
            precio_actual = precios[s]

            pnl = (precio_actual - pos["entry"]) / pos["entry"]

            # Take profit
            if pnl > 0.015:
                self.cerrar(s, precio_actual, pnl)

            # Stop loss
            elif pnl < -0.02:
                self.cerrar(s, precio_actual, pnl)

    # =========================
    # COMPRAR
    # =========================
    def comprar(self, symbol, precio, prob, tipo):

        # cooldown anti-reentrada
        if symbol in self.cooldowns:
            if time.time() < self.cooldowns[symbol]:
                return False

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        # 🔥 SIN USO_CAPITAL (CORREGIDO)
        capital_operable = self.capital * (1 - config.RESERVA_CAPITAL)

        if capital_operable <= 0:
            return False

        if tipo == "elite":
            inversion = capital_operable * config.RIESGO_ELITE
        else:
            inversion = capital_operable * config.RIESGO_NORMAL

        if inversion <= 10:
            return False

        if inversion > self.capital:
            return False

        self.capital -= inversion

        self.posiciones[symbol] = {
            "entry": precio,
            "inversion": inversion,
            "prob": prob,
            "tipo": tipo
        }

        print(f"🟢 BUY {symbol} ${round(inversion,2)} | {tipo}")

        return True

    # =========================
    # CERRAR
    # =========================
    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones.pop(symbol)

        resultado = pos["inversion"] * (1 + pnl)
        self.capital += resultado

        # IA aprende
        if pnl > 0:
            self.win += 1
        else:
            self.loss += 1

        # cooldown anti-recompra
        self.cooldowns[symbol] = time.time() + config.COOLDOWN_SYMBOL

        print(f"🔴 SELL {symbol} pnl {round(pnl,4)}")

    # =========================
    def data(self):
        return {
            "capital": round(self.capital, 2),
            "posiciones": self.posiciones,
            "win": self.win,
            "loss": self.loss
        }


portfolio = Portfolio()