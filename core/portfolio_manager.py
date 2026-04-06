import numpy as np

def asignar_capital(signals, capital, max_posiciones=5):

    # signals = [(symbol, score, prob)]
    signals = sorted(signals, key=lambda x: x[2], reverse=True)[:max_posiciones]

    total_score = sum([s[2] for s in signals])

    allocation = {}

    for symbol, score, prob in signals:
        peso = prob / total_score if total_score > 0 else 0
        allocation[symbol] = capital * peso

    return allocation