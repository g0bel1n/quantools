from typing import List, Optional, Tuple, Union

import pandas as pd
import numpy as np
from scipy.special import binom
from functools import partial

from .dataprocessor import DataProcessor
from ._utils import isStationnary


class FractionalDiff(DataProcessor):
    def __init__(self) -> None:
        super().__init__()

        self.valid_method: List[str] = ["fixed-window"]

    def _diff(
        self, X: pd.Series, order: Union[float, int], window_size: int = 10
    ) -> pd.Series:

        _X = X.copy(deep=True)
        if order == 1:
            _X = X - X.shift(int(order))

        else:
            coeffs = (-1) ** np.arange(window_size) * binom(
                order, np.arange(window_size)
            )
            D = partial(np.convolve, coeffs, mode="valid")
            _X = _X.rolling(window_size).apply(D, raw=True)

        return _X

    def _autodiff(self, X: pd.Series, precision: float):
        """
        It takes a series and a precision, and returns the differenced series and the order of differencing

        :param X: pd.Series
        :type X: pd.Series
        :param precision: the precision of the autodiff function
        :type precision: float
        :return: The difference between the current value and the previous value.
        """
        a, b = 0, 4
        if isStationnary(X):
            return X, 0
        _valid = []
        while b - a >= precision:
            mid = (b + a) / 2
            _X = X.copy(deep=True)
            if isStationnary((diff_serie := self._diff(_X, order=mid))):
                _valid.append((diff_serie, mid))
                # print(f"Found a valid order of differencing: {mid}")
                b = mid
            else:
                # print(f"Order of differencing {mid} is not valid")
                a = mid

        if len(_valid) == 0:
            raise ValueError("Could not find a valid order of differencing")
        return _valid[-1]

    def _1D_diff(
        self,
        X: pd.Series,
        precision: float,
        method: str = "fixed-window",
        order: Optional[Union[float, int]] = None,
    ):
        if order is not None:
            return self._diff(X, order=order), order

        else:
            return self._autodiff(X, precision=precision)

    def __call__(
        self,
        X: Union[pd.Series, pd.DataFrame],
        precision: float = 0.1,
        method: str = "fixed-window",
        order: Optional[Union[float, int]] = None,
        return_order: bool = False,
        rename: bool = True,
    ) -> Union[
        Tuple[Union[pd.Series, pd.DataFrame], List[float]],
        Union[pd.Series, pd.DataFrame],
    ]:
        assert method in self.valid_method, ValueError(
            f"The method must be in {self.valid_method}"
        )

        assert order is None or order > 0, ValueError("The order must be positive")

        if isinstance(X, pd.DataFrame) and X.shape[1] > 1:
            cols_name = (
                [f"{el}_stationnarized" for el in X.columns] if rename else X.columns
            )
            for col in range(X.shape[1]):
                X_diff_, order_ = self._1D_diff(
                    X.iloc[:, col], precision, method, order
                )
                try:
                    X_diff = pd.concat((X_diff, X_diff_), axis=1)
                    orders.append(order_)
                except UnboundLocalError:
                    X_diff = X_diff_
                    orders = [order_]
            X_diff.columns = cols_name

        else:
            X_diff, orders = self._1D_diff(X, precision, method, order)

        return (X_diff, orders) if return_order else X_diff
