def asignar_capital(candidatos, capital_total, max_posiciones):

    # candidatos: [(symbol, score, prob, precio)]

    # ordenar por probabilidad (mejor primero)
    candidatos = sorted(candidatos, key=lambda x: x[2], reverse=True)

    # seleccionar top
    seleccion = candidatos[:max_posiciones]

    # suma de probabilidades
    total_prob = sum([c[2] for c in seleccion])

    allocation = {}

    for symbol, score, prob, precio in seleccion:

        if total_prob == 0:
            peso = 1 / len(seleccion)
        else:
            peso = prob / total_prob

        allocation[symbol] = {
            "capital": capital_total * peso,
            "precio": precio
        }

    return allocation