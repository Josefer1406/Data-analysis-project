import numpy as np
import config

def optimizar_portafolio(candidatos, capital_total, max_posiciones):

    # 🔥 PROTECCIÓN
    if capital_total < config.MIN_CAPITAL_OPERAR:
        return {}

    candidatos = sorted(candidatos, key=lambda x: x[2], reverse=True)
    candidatos = candidatos[:max_posiciones]

    probs = np.array([c[2] for c in candidatos])
    probs = np.clip(probs, 0.01, 1)

    pesos = probs / probs.sum()

    allocation = {}

    for i, (symbol, score, prob, precio) in enumerate(candidatos):

        capital_asignado = capital_total * pesos[i]

        # 🔥 evitar tamaños ridículos
        if capital_asignado < 10:
            continue

        allocation[symbol] = {
            "capital": capital_asignado,
            "precio": precio,
            "peso": pesos[i]
        }

    return allocation