import pandas as pd

def filtrar_correlacion(precios_dict, threshold=0.8):

    df = pd.DataFrame(precios_dict)

    if df.shape[1] < 2:
        return list(precios_dict.keys())

    corr = df.pct_change().corr()

    seleccionados = []

    for col in corr.columns:

        alta_corr = False

        for sel in seleccionados:
            if corr.loc[col, sel] > threshold:
                alta_corr = True
                break

        if not alta_corr:
            seleccionados.append(col)

    return seleccionados