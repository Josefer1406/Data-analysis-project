import numpy as np

def optimizar_portafolio(candidatos, capital_total, max_posiciones):
    """
    candidatos = [(symbol, score, prob, precio)]
    """

    # ordenar por probabilidad
    candidatos = sorted(candidatos, key=lambda x: x[2], reverse=True)
    candidatos = candidatos[:max_posiciones]

    # extraer probabilidades
    probs = np.array([c[2] for c in candidatos])

    # evitar ceros
    probs = np.clip(probs, 0.01, 1)

    # normalizar
    pesos = probs / probs.sum()

    allocation = {}

    for i, (symbol, score, prob, precio) in enumerate(candidatos):

        capital_asignado = capital_total * pesos[i]

        allocation[symbol] = {
            "capital": capital_asignado,
            "precio": precio,
            "peso": pesos[i]
        }

    return allocation