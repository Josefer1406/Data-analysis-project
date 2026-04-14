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
            return 0.75  # más conservador

        if winrate > 0.6:
            return 0.65  # más agresivo

        return config.PROB_MIN

    # =========================
    # ACTUALIZAR
    # =========================
    def actualizar(self, precios):

        for s in list(self.posiciones.keys()):

            if s not in precios:
                continue

            pos = self.posiciones[s]
            precio_actual = precios[s]

            pnl = (precio_actual - pos["entry"]) / pos["entry"]

            # TP
            if pnl > 0.015:
                self.cerrar(s, precio_actual, pnl)

            # SL
            elif pnl < -0.02:
                self.cerrar(s, precio_actual, pnl)

    # =========================
    # COMPRAR
    # =========================
    def comprar(self, symbol, precio, prob, tipo):

        # cooldown activo
        if symbol in self.cooldowns:
            if time.time() < self.cooldowns[symbol]:
                return False

        if symbol in self.posiciones:
            return False

        capital_disponible = self.capital * (1 - config.RESERVA_CAPITAL)

        if capital_disponible <= 0:
            return False

        if tipo == "elite":
            inversion = capital_disponible * config.RIESGO_ELITE
        else:
            inversion = capital_disponible * config.RIESGO_NORMAL

        if inversion <= 10:
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

        # IA aprendizaje
        if pnl > 0:
            self.win += 1
        else:
            self.loss += 1

        # cooldown
        self.cooldowns[symbol] = time.time() + config.COOLDOWN_SYMBOL

        print(f"🔴 SELL {symbol} pnl {round(pnl,4)}")

    # =========================
    def data(self):
        return {
            "capital": self.capital,
            "posiciones": self.posiciones,
            "win": self.win,
            "loss": self.loss
        }


portfolio = Portfolio()