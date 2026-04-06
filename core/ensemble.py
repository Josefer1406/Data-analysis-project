def decision_ensemble(signals, ml_prob):

    score = sum(signals)

    # peso ML fuerte
    if ml_prob > 0.65:
        score += 2

    if score >= 3:
        return "BUY"
    else:
        return "HOLD"