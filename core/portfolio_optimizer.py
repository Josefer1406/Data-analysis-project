import numpy as np
import config

def optimizar_portafolio(candidatos, capital_total, max_posiciones):

    if capital_total < config.MIN_CAPITAL_OPERAR:
        return {}

    candidatos = sorted(candidatos, key=lambda x: x[2], reverse=True)
    candidatos = candidatos[:max_posiciones]

    probs = np.array([c[2] for c in candidatos])

    # 🔥 penalizar probabilidades medias
    probs = np.power(probs, 2)

    probs = np.clip(probs, 0.01, 1)

    pesos = probs / probs.sum()

    allocation = {}

    for i, (symbol, score, prob, precio) in enumerate(candidatos):

        capital_asignado = float(capital_total * pesos[i])

        # 🔥 límite institucional (MUY IMPORTANTE)
        max_capital_asset = capital_total * 0.3

        capital_asignado = min(capital_asignado, max_capital_asset)

        # 🔥 mínimo realista
        if capital_asignado < 30:
            continue

        allocation[symbol] = {
            "capital": capital_asignado,
            "precio": float(precio),
            "peso": float(pesos[i]),
            "conviccion": float(prob)
        }

    return allocation