import pandas as pd

def filtrar_correlacion(precios_dict, threshold=0.75):

    df = pd.DataFrame(precios_dict)

    if df.shape[1] < 2:
        return list(precios_dict.keys())

    corr = df.pct_change().corr()

    seleccionados = []

    for col in corr.columns:

        if not seleccionados:
            seleccionados.append(col)
            continue

        correlacion_alta = False

        for sel in seleccionados:
            if corr.loc[col, sel] > threshold:
                correlacion_alta = True
                break

        if not correlacion_alta:
            seleccionados.append(col)

    return seleccionados