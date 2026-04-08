import time
import config

class Portfolio:
    def __init__(self):
        self.capital = config.CAPITAL_INICIAL
        self.posiciones = {}
        self.cooldowns = {}

        # 🔥 DEBUG INSTITUCIONAL (capital inicial real)
        print(f"🚀 Capital inicial: {self.capital}")

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
        # 🔒 límite de posiciones
        if len(self.posiciones) >= config.MAX_POSICIONES:
            return

        # ⏳ cooldown por activo
        if not self.puede_operar(symbol):
            return

        size = self.calcular_size(prob)

        # 💰 capital mínimo
        if size < config.MIN_CAPITAL_OPERAR:
            return

        # 🛑 evitar duplicar posición
        if symbol in self.posiciones:
            return

        self.posiciones[symbol] = {
            "precio": precio,
            "size": size
        }

        self.capital -= size
        self.set_cooldown(symbol, prob)

        print(f"🟢 BUY {symbol} | ${size:.2f} | prob: {prob:.2f}")

    def vender(self, symbol, precio):
        if symbol not in self.posiciones:
            return

        posicion = self.posiciones[symbol]
        pnl = (precio - posicion["precio"]) / posicion["precio"]

        # 🎯 salida institucional
        if pnl <= config.STOP_LOSS or pnl >= config.TAKE_PROFIT:
            resultado = posicion["size"] * (1 + pnl)
            self.capital += resultado

            print(f"💰 CERRAR {symbol} | pnl: {pnl:.4f} | capital: {self.capital:.2f}")

            del self.posiciones[symbol]

    def estado(self):
        return {
            "capital": round(self.capital, 2),
            "posiciones": list(self.posiciones.keys())
        }