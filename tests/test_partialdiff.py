import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import seaborn as sns

print(os.path.realpath(""))
print(os.listdir())
from quantools import PartialDiff

sns.set()


def test_PartialDiff(n_col: int = 10):
    raw_X = np.random.normal(size=(200, n_col))
    cols_name = [f"col_{i}" for i in range(n_col)]
    X = pd.DataFrame(np.cumsum(raw_X, axis=0), columns=cols_name)
    for i in range(X.shape[1]):
        X.iloc[:, i] = np.cumsum(i * 0.01 * X.iloc[:, i])
    diff = PartialDiff()
    X_diff, orders = diff(X, return_order=True, precision=1e-3)
    assert all(np.array(orders) > 0) and len(orders) == n_col and len(np.unique(orders)>1


if __name__ == "__main__":
    test_PartialDiff()
