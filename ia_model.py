import json
import os

IA_FILE = "ia_model.json"


def cargar_modelo():
    if os.path.exists(IA_FILE):
        with open(IA_FILE, "r") as f:
            return json.load(f)

    return {
        "trades": [],
        "winrate": 0.5
    }


def guardar_modelo(data):
    with open(IA_FILE, "w") as f:
        json.dump(data, f)


modelo = cargar_modelo()


def registrar_trade(features, pnl):

    resultado = 1 if pnl > 0 else 0

    modelo["trades"].append({
        "features": features,
        "resultado": resultado
    })

    modelo["trades"] = modelo["trades"][-200:]

    wins = sum(t["resultado"] for t in modelo["trades"])
    total = len(modelo["trades"])

    modelo["winrate"] = wins / total if total > 0 else 0.5

    guardar_modelo(modelo)


def score_ia(features):

    if len(modelo["trades"]) < 20:
        return 0.5

    similares = []

    for t in modelo["trades"]:
        f = t["features"]

        if abs(f["prob"] - features["prob"]) < 0.1:
            similares.append(t)

    if not similares:
        return modelo["winrate"]

    wins = sum(t["resultado"] for t in similares)

    return wins / len(similares)