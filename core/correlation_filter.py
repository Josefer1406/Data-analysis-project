import numpy as np

def filtrar_correlacion(df_prices, threshold=0.8):

    # correlación entre activos
    corr = df_prices.pct_change().corr()

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