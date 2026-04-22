import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

MODEL_FILE = "ml_model.pkl"


class MLModel:

    def __init__(self):
        self.model = None
        self.X = []
        self.y = []

        self.load()

    def load(self):
        if os.path.exists(MODEL_FILE):
            self.model = joblib.load(MODEL_FILE)
        else:
            self.model = LogisticRegression()

    def save(self):
        joblib.dump(self.model, MODEL_FILE)

    def add_sample(self, features, resultado):

        x = [
            features["momentum_5"],
            features["momentum_15"],
            features["momentum_1h"],
            features["trend"],
            features["vol_ratio"],
            features["volatility"]
        ]

        self.X.append(x)
        self.y.append(1 if resultado > 0 else 0)

        # limitar dataset
        self.X = self.X[-500:]
        self.y = self.y[-500:]

        if len(self.X) > 50:
            self.train()

    def train(self):
        try:
            self.model.fit(self.X, self.y)
            self.save()
        except:
            pass

    def predict(self, features):

        x = np.array([[
            features["momentum_5"],
            features["momentum_15"],
            features["momentum_1h"],
            features["trend"],
            features["vol_ratio"],
            features["volatility"]
        ]])

        try:
            prob = self.model.predict_proba(x)[0][1]
            return float(prob)
        except:
            return 0.5


ml_model = MLModel()