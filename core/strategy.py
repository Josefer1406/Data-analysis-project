import numpy as np

def trend_following(last):
    return 1 if last["ema20"] > last["ema50"] else 0

def mean_reversion(last):
    return 1 if last["rsi"] < 30 else 0

def momentum(last):
    return 1 if last["rsi"] > 55 else 0

def volatility_filter(last):
    return 1 if last["volatilidad"] < 0.05 else 0