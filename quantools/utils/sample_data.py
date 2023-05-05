import numpy as np
import pandas as pd

import quantools as qt


def generate_brownian_prices(
    n_timeseries: int,
    n_periods: int,
    drift: float = 0,
    vol: float = 1,
    s0: float = 1,
    dt=1,
):
    """

    It generates a table of prices for a given number of assets, with a given number of periods, and a
    given drift and volatility

    :param n_timeseries: the number of timeseries to generate
    :param n_periods: The number of periods to generate
    :type n_periods: int
    :param drift: the mean of the increments, defaults to 0
    :type drift: float (optional)
    :param vol: the volatility of the underlying asset, defaults to 1
    :type vol: float (optional)
    :param s0: the initial price of the asset, defaults to 1
    :type s0: float (optional)
    :param dt: The time step, defaults to 1 (optional)
    :return: A table with the prices of the assets, the index is the timestamps and the columns are the
    assets.
    """

    # Generate Brownian motion increments.

    increments = np.random.normal(
        loc=drift * dt, scale=vol * np.sqrt(dt), size=(n_periods, n_timeseries)
    )
    increments = increments.reshape((n_periods, n_timeseries))

    # Generate Brownian motion prices.

    prices = s0 * np.exp(np.cumsum(increments, axis=0))

    timestamps = pd.date_range(start="2020-01-01", periods=n_periods, freq="1D")

    return qt.Table(
        prices, index=timestamps, columns=[f"asset_{i}" for i in range(n_timeseries)]
    )


def generate_brownian_returns(
    n_timeseries: int, n_periods: int, drift: float = 0, vol: float = 1, dt=1
):
    """
    It generates a table of returns for a given number of time series, with a given number of periods,
    and a given drift and volatility

    :param n_timeseries: the number of timeseries to generate
    :type n_timeseries: int
    :param n_periods: the number of periods to generate
    :type n_periods: int
    :param drift: the expected return of the asset, defaults to 0
    :type drift: float (optional)
    :param vol: the volatility of the returns, defaults to 1
    :type vol: float (optional)
    :param dt: The time step of the simulation, defaults to 1 (optional)
    :return: A table with returns, index, and columns
    """

    increments = np.random.normal(
        loc=drift * dt, scale=vol * np.sqrt(dt), size=(n_periods, n_timeseries)
    ).reshape((n_periods, n_timeseries))

    prices = np.exp(np.cumsum(increments, axis=0))

    returns = prices[1:, :] / prices[:-1, :] - 1

    timestamps = pd.date_range(start="2020-01-01", periods=n_periods - 1, freq="1D")

    return qt.Table(
        returns,
        index=timestamps,
        columns=[f"returns_asset_{i}" for i in range(n_timeseries)],
    )
