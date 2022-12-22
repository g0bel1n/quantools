import numpy as np
import pandas as pd

from quantools import FractionalDiff, generate_brownian_prices


def test_FractionalDiff(n_col: int = 10):
    X_1 = generate_brownian_prices(
        n_timeseries=n_col // 2, n_periods=200, drift=1e-2, vol=1e-3, s0=1, dt=1
    )
    X_2 = generate_brownian_prices(
        n_timeseries=n_col // 2, n_periods=200, drift=1e-6, vol=1e-3, s0=1, dt=1
    )
    X = pd.concat([X_1, X_2], axis=1)

    diff = FractionalDiff()
    _, orders = diff(X, return_order=True, precision=1e-6)
    assert len(orders) == n_col and len(np.unique(orders)) > 1


if __name__ == "__main__":
    test_FractionalDiff()
