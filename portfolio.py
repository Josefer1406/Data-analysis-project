import time
import config

class Portfolio:
    def __init__(self):
        self.capital = config.CAPITAL_INICIAL
        self.posiciones = {}
        self.cooldowns = {}

    def cooldown_dinamico(self, prob):
        if prob > 0.9:
            return 30
        elif prob > 0.8:
            return 60
        else:
            return config.COOLDOWN_BASE

    def puede_operar(self, symbol):
        ahora = time.time()
        return symbol not in self.cooldowns or ahora >= self.cooldowns[symbol]

    def set_cooldown(self, symbol, prob):
        self.cooldowns[symbol] = time.time() + self.cooldown_dinamico(prob)

    def calcular_size(self, prob):
        capital_disponible = self.capital * (1 - config.RESERVA_CAPITAL)

        if prob > 0.9:
            return capital_disponible * config.RIESGO_MAXIMO_POR_TRADE
        elif prob > 0.8:
            return capital_disponible * config.RIESGO_MEDIO
        else:
            return capital_disponible * config.RIESGO_BAJO

    def comprar(self, symbol, precio, prob):
        if len(self.posiciones) >= config.MAX_POSICIONES:
            return

        if not self.puede_operar(symbol):
            return

        size = self.calcular_size(prob)

        if size < config.MIN_CAPITAL_OPERAR:
            return

        self.posiciones[symbol] = {
            "precio": precio,
            "size": size
        }

        self.capital -= size
        self.set_cooldown(symbol, prob)

        print(f"🟢 BUY {symbol} | ${size:.2f} | prob: {prob}")

    def vender(self, symbol, precio):
        if symbol not in self.posiciones:
            return

        posicion = self.posiciones[symbol]
        pnl = (precio - posicion["precio"]) / posicion["precio"]

        if pnl <= config.STOP_LOSS or pnl >= config.TAKE_PROFIT:
            self.capital += posicion["size"] * (1 + pnl)
            print(f"💰 CERRAR {symbol} | pnl: {pnl:.4f}")
            del self.posiciones[symbol]

    def estado(self):
        return {
            "capital": self.capital,
            "posiciones": list(self.posiciones.keys())
        }