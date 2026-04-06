class RiskEngine:

    def __init__(self):
        self.max_drawdown = 0.25
        self.max_risk_trade = 0.02

    def controlar_drawdown(self, capital, peak):

        dd = (capital - peak) / peak

        if dd < -self.max_drawdown:
            return False

        return True

    def ajustar_riesgo(self, capital, peak):

        dd = (capital - peak) / peak

        # reduce riesgo en pérdidas
        if dd < -0.1:
            return 0.01

        return self.max_risk_trade