import config
import numpy as np

class Portfolio:

    def __init__(self):
        self.capital = config.CAPITAL_INICIAL
        self.posiciones = {}  # {symbol: {precio, capital}}
        self.historial = []

    # ============================
    # 🧠 CORRELACIÓN SIMPLE (PROXY)
    # ============================
    def correlacion_alta(self, symbol, posiciones_actuales):
        # Proxy simple: evita duplicar tipo de activo (L1)
        base = symbol.split("/")[0]

        for pos in posiciones_actuales:
            if pos.split("/")[0] == base:
                return True

        return False

    # ============================
    # 📊 POSITION SIZING PRO
    # ============================
    def calcular_peso(self, prob):

        if prob >= 0.80:
            return config.MAX_PESO_EXCELENTE   # 30%
        elif prob >= 0.65:
            return config.MAX_PESO_BUENO       # 20%
        else:
            return config.MAX_PESO_NORMAL      # 15%

    # ============================
    # 🧠 FILTRO DE ENTRADA
    # ============================
    def puede_comprar(self, symbol, prob):

        if prob < config.MIN_PROBABILIDAD:
            return False

        if symbol in self.posiciones:
            return False

        if len(self.posiciones) >= config.MAX_POSICIONES:
            return False

        if self.correlacion_alta(symbol, self.posiciones):
            return False

        if self.capital < config.MIN_CAPITAL_OPERAR:
            return False

        return True

    # ============================
    # 🏆 CONSTRUCCIÓN PORTAFOLIO
    # ============================
    def construir_portafolio(self, oportunidades):

        oportunidades = sorted(oportunidades, key=lambda x: x[2], reverse=True)

        portafolio = {}

        capital_disponible = self.capital * config.MAX_EXPOSICION_TOTAL

        for symbol, score, prob, precio in oportunidades:

            if not self.puede_comprar(symbol, prob):
                continue

            peso = self.calcular_peso(prob)

            capital_asignado = capital_disponible * peso

            if capital_asignado > self.capital:
                capital_asignado = self.capital

            portafolio[symbol] = {
                "capital": float(capital_asignado),
                "precio": float(precio),
                "peso": float(peso),
                "conviccion": float(prob)
            }

        return portafolio

    # ============================
    # 🟢 EJECUCIÓN DE COMPRA
    # ============================
    def ejecutar_compras(self, portafolio):

        for symbol, data in portafolio.items():

            if symbol in self.posiciones:
                continue

            if self.capital <= 0:
                break

            capital = data["capital"]

            if capital > self.capital:
                capital = self.capital

            self.posiciones[symbol] = {
                "precio": data["precio"],
                "capital": capital
            }

            self.capital -= capital

            print(f"🟢 BUY {symbol} | convicción: {data['conviccion']:.2f}")

    # ============================
    # 🔴 CONTROL DE SALIDA (PRO)
    # ============================
    def evaluar_salidas(self, precios_actuales):

        eliminar = []

        for symbol, pos in self.posiciones.items():

            precio_actual = precios_actuales.get(symbol)

            if not precio_actual:
                continue

            pnl = (precio_actual - pos["precio"]) / pos["precio"]

            print(f"🔍 {symbol} pnl: {round(pnl,4)}")

            # STOP LOSS
            if pnl <= -config.STOP_LOSS:
                print(f"🔴 STOP LOSS {symbol}")
                self.capital += pos["capital"]
                eliminar.append(symbol)

            # TAKE PROFIT DINÁMICO
            elif pnl >= config.TAKE_PROFIT:
                print(f"💰 TAKE PROFIT {symbol}")
                self.capital += pos["capital"]
                eliminar.append(symbol)

        for symbol in eliminar:
            del self.posiciones[symbol]

    # ============================
    # 📊 ESTADO
    # ============================
    def resumen(self):
        print(f"💰 Capital: {self.capital}")
        print(f"📊 Posiciones: {list(self.posiciones.keys())}")