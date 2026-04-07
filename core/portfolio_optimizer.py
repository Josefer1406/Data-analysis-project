import numpy as np
import config

def optimizar_portafolio(candidatos, capital_total, max_posiciones):

    if not candidatos:
        return {}

    allocation = {}

    # 🔥 Ordenar por probabilidad (convicción)
    candidatos = sorted(candidatos, key=lambda x: x[2], reverse=True)

    capital_disponible = capital_total

    total_asignado = 0
    posiciones = 0

    for symbol, score, prob, precio in candidatos:

        if posiciones >= max_posiciones:
            break

        # 🚫 NO TRADE SI NO HAY EDGE
        if prob < 0.6:
            continue

        # 🎯 CLASIFICACIÓN INSTITUCIONAL
        if prob >= 0.9:
            peso = 0.30   # 🔥 EXCELENTE
        elif prob >= 0.75:
            peso = 0.20   # buena
        else:
            peso = 0.15   # normal

        # 🚫 CONTROL DE RIESGO GLOBAL
        if total_asignado + peso > 0.60:
            break

        capital_asignado = capital_total * peso

        allocation[symbol] = {
            "capital": float(capital_asignado),
            "precio": float(precio),
            "peso": float(peso),
            "conviccion": float(prob)
        }

        total_asignado += peso
        posiciones += 1

    return allocation