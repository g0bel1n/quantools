import pandas as pd
from pandas import DataFrame, Series
import os
import logging
import numpy as np
from typing import Optional, Union
import re

import quantools as qt

from bokeh.plotting import figure, show
from bokeh.models import TabPanel, Tabs



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


@assert_ts
def sharpe(self, start=None, end=None, risk_free=0):
    _daily = self.resample("1D").last()
    _E = _daily.loc[start:end].mean() * 252 - risk_free
    _std = _daily.loc[start:end].std() * np.sqrt(252)
    return _E / _std


@assert_ts
def sortino(self, start=None, end=None, risk_free=0):
    _daily = self.resample("1D").last()
    _E = _daily.loc[start:end].mean() * 252 - risk_free
    _std_neg = _daily[_daily < 0].loc[start:end].std() * np.sqrt(252)
    return _E / _std_neg


@assert_ts
def drawdown(self, start=None, end=None):
    _daily = self.resample("1D").last()
    _cummax = _daily.loc[start:end].cummax()
    return (_daily.loc[start:end] - _cummax) / _cummax


@assert_ts
def max_drawdown(self, start=None, end=None, risk_free=0):
    return self.drawdown(start, end).min()


@assert_ts
def calmar(self, start=None, end=None, risk_free=0):
    _daily = self.resample("1D").last()
    _E = _daily.loc[start:end].mean() * 252 - risk_free
    _max_drawdown = abs(self.max_drawdown(start, end))
    print(_E, _max_drawdown)
    return _E / _max_drawdown


@assert_ts
def indicators(self, start=None, end=None, risk_free=0):
    indicators_names, indicators_values = [], []
    for indicator in __available_indicators__:
        indicators_names.append(indicator)
        indicators_values.append(getattr(self, indicator)(start, end, risk_free))

    return pd.DataFrame(indicators_values, index=indicators_names, columns=["value"])


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

    drawdown = drawdown

    max_drawdown = max_drawdown

    indicators = indicators

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
        index=None,
        columns=None,
        dtype=None,
        copy=False,
        ts=True,
        verbose=False,
        header=None,
    ):  # sourcery skip: low-code-quality

        if isinstance(data, str):
            filetype = data.split(".")[-1]
            if filetype not in __authorized_filetype__:
                raise ValueError(f"Filetype {filetype} is not supported")

            if os.path.getsize(data) > 100e6:
                chunksize = 1e6
                logger.warning(f"File is too big, chunksize is set to {chunksize}")
            else:
                chunksize = None

            if filetype == "csv":
                super().__init__(pd.read_csv(data, chunksize=chunksize, header=header))
            elif filetype == "json":
                super().__init__(pd.read_json(data, chunksize=chunksize, header=header))
            elif filetype == "excel":
                super().__init__(
                    pd.read_excel(
                        data,
                    )
                )
            elif filetype == "txt":
                super().__init__(
                    pd.read_csv(data, sep=",", chunksize=chunksize, header=header)
                )
        else:
            super().__init__(
                data=data, index=index, columns=columns, dtype=dtype, copy=copy
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

        if ts and not pd.api.types.is_datetime64_any_dtype(self.index):
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
            if not found:
                logger.info("No datetime column found")

    def __type__(self):
        return "Table"

    def __repr__(self):
        return f"Table({super().__repr__()})"

    def __str__(self):
        return f"Table({super().__str__()})"

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
        self.loc[:, num.columns] = diff_[0] if return_order else diff_
        return None

    def normalize(self, inplace=False):
        num = self.select_dtypes(include="number")

        if not inplace:
            return (num - num.mean()) / num.std()

        self.is_normalized = True

        self.loc[:, num.columns] = (num - num.mean()) / num.std()
        return None

    def as_df(self):
        return pd.DataFrame(self)

    sharpe = sharpe

    calmar = calmar

    sortino = sortino

    drawdown = drawdown

    max_drawdown = max_drawdown

    indicators = indicators

    def autoplot(self, **kwargs):
        tabs = [
            TabPanel(child=qt.plot(self[col], **kwargs), title=col)
            for col in self.columns
            if pd.api.types.is_numeric_dtype(self[col])
        ]
        show(Tabs(tabs=tabs))
        

               

