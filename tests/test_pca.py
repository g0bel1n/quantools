from quantools import PCA, generate_brownian_prices
import numpy as np


def test_pca():
    order = np.random.randint(1, 10)
    n_dim = np.random.randint(1, 10)

    X = generate_brownian_prices(
        n_timeseries=n_dim, n_periods=1000, drift=1e-3, vol=1e-2
    )

    pca = PCA(order=order)

    X_pca = pca(X)

    assert X_pca.shape[1] == order
    assert X_pca.shape[0] == X.shape[0]
    assert X_pca.index.equals(X.index)
