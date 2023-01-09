import pandas as pd
from pandas import DataFrame, Series
import os
import logging
import numpy as np
from typing import Optional, Union
import re

import quantools as qt

from bokeh.plotting import show
from bokeh.models import TabPanel, Tabs


# !!!! uses ddof=0 in std calculation


logger = logging.getLogger(__name__)

__authorized_filetype__ = ["csv", "json", "excel", "txt"]

__available_indicators__ = ["sharpe", "sortino", "calmar", "max_drawdown"]


def return_Table(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return (
            Table(result, verbose=False)
            if isinstance(result, (DataFrame, Series))
            else result
        )

    return wrapper


def assert_ts(func):
    def wrapper(*args, **kwargs):
        if not isinstance(args[0], Table) and not isinstance(args[0], TableSeries):
            raise ValueError("Method can only be applied to Table object")
        if not pd.api.types.is_datetime64_any_dtype(args[0].index):
            raise ValueError("Method can only be applied to Table with datetime index")
        return func(*args, **kwargs)

    return wrapper


def daily_resampler(self):
    _a = self.resample("1D").last()
    _a = _a.fillna(method="ffill")  # if oversampling
    return _a


@assert_ts
def sharpe(self, start=None, end=None, risk_free=0):
    _daily = daily_resampler(self)
    _E = _daily.loc[start:end].mean() * 252 - risk_free
    _std = _daily.loc[start:end].std(ddof=0) * np.sqrt(252)
    return _E / _std


@assert_ts
def sortino(self, start=None, end=None, risk_free=0):
    _daily = daily_resampler(self)
    _E = _daily.loc[start:end].mean() * 252 - risk_free
    _std_neg = _daily[_daily < 0].loc[start:end].std(ddof=0) * np.sqrt(252)
    return _E / _std_neg


@assert_ts
def drawdowns(self, start=None, end=None):
    _daily = daily_resampler(self)
    _price = (_daily.loc[start:end] + 1).cumprod() - 1
    _cummax = _price.cummax()
    return _cummax - _price


@assert_ts
def max_drawdown(self, start=None, end=None, risk_free=0):
    return self.drawdowns(start, end).max()


@assert_ts
def calmar(self, start=None, end=None, risk_free=0):
    # not annualized
    _daily = daily_resampler(self)
    _E = _daily.loc[start:end].mean() - risk_free
    _max_drawdown = abs(self.max_drawdown(start, end))
    return _E / _max_drawdown


@assert_ts
def indicators(self, start=None, end=None, risk_free=0):
    indicators_names, indicators_values = [], []
    for indicator in __available_indicators__:
        indicators_names.append(indicator)
        indicators_values.append(getattr(self, indicator)(start, end, risk_free))

    return pd.DataFrame(indicators_values, index=indicators_names, columns=["value"])


@assert_ts
def cumulative(self, start=None, end=None):
    return (self.loc[start:end] + 1).cumprod() - 1


class TableSeries(Series):
    @property
    def _constructor(self):
        return TableSeries

    @property
    def _constructor_expanddim(self):
        return Table

    sharpe = sharpe

    calmar = calmar

    sortino = sortino

    drawdowns = drawdowns

    max_drawdown = max_drawdown

    indicators = indicators

    cumulative = cumulative

    def as_df(self):
        return pd.Series(self)

    def autoplot(self, **kwargs):
        return show(qt.plot(self, **kwargs))


class Table(DataFrame):
    @property
    def _constructor(self):
        return Table

    @property
    def _constructor_sliced(self):
        return TableSeries

    def __init__(
        self,
        data=None,
        dtype=None,
        copy=False,
        ts=True,
        verbose=False,
        parse_dates=False,
        is_str_data=False,
        **kwargs,
    ):  # sourcery skip: low-code-quality

        if isinstance(data, str):
            filetype = data.split(".")[-1]
            if filetype not in __authorized_filetype__ or not is_str_data:
                raise ValueError(f"Filetype {filetype} is not supported")
            print(is_str_data)
            if filetype == "csv":
                data = pd.read_csv(data, **kwargs)
            elif filetype == "json":
                data = pd.read_json(data, **kwargs)
            elif filetype == "excel":
                data = pd.read_excel(data, **kwargs)

            elif filetype == "txt":
                data = pd.read_csv(data, sep=",", **kwargs)
            super().__init__(data)
        elif is_str_data:
            data = pd.read_csv(data, **kwargs)
            super().__init__(data)

        else:
            super().__init__(
                data=data, dtype=dtype, copy=copy, **kwargs  # type: ignore
            )

        self.is_stationnary = False
        self.is_normalized = False
        nb_rows, nb_cols = self.shape

        if verbose:
            print(f"Table has {nb_rows} rows and {nb_cols} columns")
            print(f"Table has {self.memory_usage().sum()/1e6} MB of memory")
            print(f"Table columns are {[*self.columns]}")
            nb_nan = self.isna().sum().sum()
            if nb_nan > 0:
                logger.warning(f"Table contains {nb_nan} NaN values")
            else:
                print("Table has no NaN values")

        if ts and not pd.api.types.is_datetime64_any_dtype(self.index) and parse_dates:
            found = False
            for col in self.columns:
                first_value = self[col][0]
                if isinstance(first_value, str):
                    if re.match(r"\d{4}-\d{2}-\d{2}", first_value) or re.match(
                        r"\d{2}/\d{2}/\d{4}", first_value
                    ):
                        self[col] = pd.to_datetime(self[col])
                        self.set_index(col, inplace=True)
                        logger.info(f"Column {col} is set as index")
                        found = True
                        break
                elif isinstance(first_value, int):
                    if first_value > 1e9:
                        self[col] = pd.to_datetime(self[col], unit="s")
                        self.set_index(col, inplace=True)
                        logger.info(f"Column {col} is set as index")
                        found = True
                        break

                elif pd.api.types.is_datetime64_any_dtype(first_value):
                    self.set_index(col, inplace=True)
                    logger.info(f"Column {col} is set as index")
                    found = True
                    break
            self.index.name = "date"
            if not found:
                logger.info("No datetime column found")

    def __type__(self):
        return "Table"

    def __repr__(self):
        return super().__repr__() + " Table Object"

    def __str__(self):
        return super().__str__() + " Table Object"

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def stationnarize(
        self,
        precision: float = 0.1,
        method: str = "fixed-window",
        order: Optional[Union[float, int]] = None,
        return_order: bool = False,
        inplace=False,
    ):
        num = self.select_dtypes(include="number")

        frac_diff = qt.FractionalDiff()

        if not inplace:
            return frac_diff(
                num,
                order=order,
                return_order=return_order,
                method=method,
                precision=precision,
                rename=False,
            )

        self.is_stationnary = True
        diff_ = frac_diff(
            num,
            order=order,
            return_order=return_order,
            method=method,
            precision=precision,
            rename=False,
        )
        self[num.columns] = diff_[0] if return_order else diff_
        return None

    def normalize(self, inplace=False):
        num = self.select_dtypes(include="number")

        if not inplace:
            return (num - num.mean()) / num.std(ddof=0)

        self.is_normalized = True

        self.loc[:, num.columns] = (num - num.mean()) / num.std(ddof=0)
        return None

    def as_df(self):
        return pd.DataFrame(self)

    sharpe = sharpe

    calmar = calmar

    sortino = sortino

    drawdowns = drawdowns

    max_drawdown = max_drawdown

    indicators = indicators

    cumulative = cumulative

    def autoplot(self, **kwargs):
        tabs = [
            TabPanel(child=qt.plot(self.loc[:, col], **kwargs), title=col)  # type: ignore weird cause TableSeries
            for col in self.columns
            if pd.api.types.is_numeric_dtype(self[col])
        ]
        show(Tabs(tabs=tabs))
