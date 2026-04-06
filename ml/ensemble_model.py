import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

class EnsembleModel:

    def __init__(self):
        self.rf = RandomForestClassifier(n_estimators=100)
        self.lr = LogisticRegression()

    def train(self, X, y):
        self.rf.fit(X, y)
        self.lr.fit(X, y)

    def predict(self, X):
        p1 = self.rf.predict_proba(X)[:,1]
        p2 = self.lr.predict_proba(X)[:,1]
        return (p1 + p2) / 2