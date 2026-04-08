import time

class Portfolio:
    def __init__(self):
        self.capital = 1000
        self.posiciones = {}
        self.historial = []
        self.trades = 0
        self.equity_curve = []

        print(f"🚀 Capital inicial: {self.capital}")

    def comprar(self, symbol, precio, prob):
        if symbol in self.posiciones:
            return

        if prob >= 0.85:
            porcentaje = 0.30
        elif prob >= 0.70:
            porcentaje = 0.20
        else:
            porcentaje = 0.10

        monto = self.capital * porcentaje

        if monto < 10:
            return

        cantidad = monto / precio

        self.capital -= monto

        self.posiciones[symbol] = {
            "precio": precio,
            "cantidad": cantidad,
            "timestamp": time.time()
        }

        print(f"🟢 BUY {symbol} | ${monto:.2f} | prob: {prob:.2f}")

    def vender(self, symbol, precio_actual):
        if symbol not in self.posiciones:
            return

        posicion = self.posiciones[symbol]

        precio_entrada = posicion["precio"]
        cantidad = posicion["cantidad"]

        pnl = (precio_actual - precio_entrada) / precio_entrada

        # TP / SL institucional
        if pnl >= 0.04 or pnl <= -0.02:

            valor = cantidad * precio_actual
            self.capital += valor
            self.trades += 1

            trade = {
                "symbol": symbol,
                "entrada": precio_entrada,
                "salida": precio_actual,
                "pnl": pnl,
                "timestamp": time.time()
            }

            self.historial.append(trade)
            self.equity_curve.append(self.capital)

            print(f"💰 SELL {symbol} | pnl: {pnl:.4f} | capital: {self.capital:.2f}")

            del self.posiciones[symbol]

    def estado(self):
        return {
            "capital": self.capital,
            "posiciones": list(self.posiciones.keys()),
            "historial": self.historial[-20:],  # últimos trades
            "trades": self.trades,
            "equity_curve": self.equity_curve
        }