from quantools import Table, TableSeries
from quantools.processing._utils import isStationnary
import pandas as pd
import numpy as np



test_table = Table("tests/data/test_table.csv", header=0)

def test_open():
    test_table = Table("tests/data/test_table.csv", header=0)
    assert isinstance(test_table, Table)


def test_sharpe():
    assert np.allclose(test_table.sharpe(), -0.087455)


def test_calmar():
    print('test_table.calmar(): ', test_table.calmar())
    assert np.allclose(test_table.calmar(), -0.000121, atol=1e-6)

def test_sortino():
    assert np.allclose(test_table.sortino(), -0.144378)


def test_max_drawdown():
    assert np.allclose(test_table.max_drawdown(), 0.443833)


def test_as_df():
    assert isinstance(test_table.as_df(), pd.DataFrame)


def test_autoplot():
    test_table.autoplot() 
    assert True

def test_normalize():
    n_test_table = test_table.normalize()
    mean, std = n_test_table.mean(), n_test_table.std()
    print(mean, std)
    assert np.allclose(mean, 0) and np.allclose(std, 1, atol=1e-3)

def test_stationnarize():
    stat_test_table = test_table.stationnarize()
    for col in stat_test_table.columns:
        assert isStationnary(stat_test_table[col])

def test_cumulative():
    cum_test_table = test_table.cumulative()
    assert True






    