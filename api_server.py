from flask import Flask, jsonify
import pandas as pd
import os

app = Flask(__name__)

ARCHIVO = "trades_log.csv"

@app.route("/")
def home():
    return "API BOT ACTIVA ✅"

@app.route("/data")
def data():

    if not os.path.exists(ARCHIVO):
        return jsonify({"error": "no data"})

    try:
        df = pd.read_csv(ARCHIVO)
        return df.to_json(orient="records")
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)