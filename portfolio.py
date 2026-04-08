import config
import time

class Portfolio:

    def __init__(self):
        self.capital_total = config.CAPITAL_INICIAL
        self.capital = config.CAPITAL_INICIAL
        self.posiciones = {}
        self.historial = []
        self.last_trade = 0

        print(f"🚀 Capital inicial: {self.capital}")

    # =========================
    # CORRELACIÓN
    # =========================
    def grupo(self, symbol):
        for g, lista in config.CORRELACION.items():
            if symbol in lista:
                return g
        return None

    def correlacion(self, symbol):
        g = self.grupo(symbol)
        for s in self.posiciones:
            if self.grupo(s) == g:
                return True
        return False

    # =========================
    # CONTROL GLOBAL
    # =========================
    def capital_usado(self):
        return sum(p["inversion"] for p in self.posiciones.values())

    def puede_operar(self):
        return (time.time() - self.last_trade) > config.COOLDOWN_BASE

    # =========================
    # APERTURA
    # =========================
    def abrir(self, signal):

        symbol = signal["symbol"]
        prob = signal["prob"]
        precio = signal["precio"]

        if not self.puede_operar():
            return

        if symbol in self.posiciones:
            return

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return

        if self.correlacion(symbol):
            return

        # 🔥 CONTROL GLOBAL 60%
        if self.capital_usado() >= self.capital_total * config.USO_CAPITAL:
            return

        # 🔥 TAMAÑO INSTITUCIONAL
        if prob >= config.UMBRAL_EXCELENTE:
            peso = config.SIZE_EXCELENTE
            tipo = "excelente"
        elif prob >= config.UMBRAL_BUENO:
            peso = config.SIZE_BUENO
            tipo = "bueno"
        else:
            return

        inversion = self.capital * peso

        if inversion < config.MIN_TRADE_USD:
            return

        cantidad = inversion / precio

        self.capital -= inversion

        self.posiciones[symbol] = {
            "precio": precio,
            "cantidad": cantidad,
            "inversion": inversion,
            "max_precio": precio,
            "tipo": tipo,
            "prob": prob,
            "trailing": False
        }

        self.last_trade = time.time()

        print(f"🟢 BUY {symbol} | ${inversion:.2f} | {tipo} | prob: {prob:.2f}")

    # =========================
    # GESTIÓN
    # =========================
    def actualizar(self, precios):

        for symbol in list(self.posiciones.keys()):

            pos = self.posiciones[symbol]
            precio = precios.get(symbol)

            if precio is None:
                continue

            pnl = (precio - pos["precio"]) / pos["precio"]

            if precio > pos["max_precio"]:
                pos["max_precio"] = precio

            # activar trailing
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
    # CIERRE
    # =========================
    def cerrar(self, symbol, precio, pnl):

        pos = self.posiciones[symbol]

        valor = pos["cantidad"] * precio
        self.capital += valor

        self.historial.append({
            "symbol": symbol,
            "tipo": pos["tipo"],
            "prob": pos["prob"],
            "pnl": pnl,
            "capital": self.capital
        })

        print(f"💰 SELL {symbol} | pnl: {pnl:.4f}")

        del self.posiciones[symbol]

    # =========================
    # DATA
    # =========================
    def data(self):

        return {
            "capital": round(self.capital, 2),
            "posiciones": self.posiciones,
            "historial": self.historial[-50:]
        }