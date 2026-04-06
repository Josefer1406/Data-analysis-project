class RiskEngine:

    def __init__(self):
        self.max_drawdown = 0.2
        self.max_risk_trade = 0.02

    def check_drawdown(self, capital, peak):
        dd = (capital - peak) / peak
        return dd > -self.max_drawdown

    def position_size(self, capital, precio):
        return (capital * self.max_risk_trade) / precio