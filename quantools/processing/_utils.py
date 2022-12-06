import pandas as pd
from statsmodels.tsa.stattools import adfuller


def isStationnary(X: pd.Series, tol: float = 0.05):
    return adfuller(X.dropna())[1] <= tol
