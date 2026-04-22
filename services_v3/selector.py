import numpy as np


# =========================
# CORRELACIÓN SIMPLE
# =========================
def correlacion(a, b):

    if len(a) < 10 or len(b) < 10:
        return 0

    return np.corrcoef(a[-20:], b[-20:])[0][1]


# =========================
# FILTRO DE CORRELACIÓN
# =========================
def filtrar_correlacion(candidatos, precios_dict, threshold=0.85):

    seleccion = []

    for asset in candidatos:

        symbol = asset["symbol"]

        correlado = False

        for s in seleccion:

            c = correlacion(
                precios_dict[s["symbol"]],
                precios_dict[symbol]
            )

            if c > threshold:
                correlado = True
                break

        if not correlado:
            seleccion.append(asset)

    return seleccion


# =========================
# SELECCIÓN FINAL
# =========================
def seleccionar_activos(candidatos, precios_dict, max_posiciones):

    # ordenar por score
    candidatos = sorted(
        candidatos,
        key=lambda x: x["score"],
        reverse=True
    )

    # filtrar correlación
    filtrados = filtrar_correlacion(candidatos, precios_dict)

    return filtrados[:max_posiciones]