import pandas as pd 
from statsmodels.tsa.stattools import adfuller
from dataprocessor import DataProcessor
from typing import Union, Tuple, List, Optional

def isStationnary(X : pd.Series, tol : float = .05):
    return adfuller(X)[1]<=tol

class PartiallDiff(DataProcessor):

    def __init__(self) -> None:
        super().__init__()

        self.valid_method : List[str] = ['fixed-window']



    def _diff(self, X : pd.Series, order: Union[float, int]) -> pd.Series:
        if order == 1:

            return X - X.shift(order)

        else :
            pass
            

    def _autodiff(self, X : pd.Series, precision: float) :
        a, b = 0, 2
        while b-a >= precision:
            mid = b+a/2
            if isStationnary((diff_serie := self._diff(X, order=mid))):
                a = mid
            else :
                b = mid

        return diff_serie, mid

    def _1D_diff(self, X : Union[pd.Series, pd.DataFrame], precision:float,  method: str = 'fixed-window',  order : Optional[Union[float, int]] = None):
        if order is not None:

            return self._diff(X, order=order), order

        else:
            return self._autodiff(X, precision=precision)
            






    def __call__(self, X : Union[pd.Series, pd.DataFrame], precision: float = .1, method: str = 'fixed-window',  order : Optional[Union[float, int]] = None, return_order : bool = False) -> Union[Tuple[Union[pd.Series, pd.DataFrame], List[float]],Union[pd.Series, pd.DataFrame]]:
        assert method in self.valid_method, ValueError(f'The method must be in {self.valid_method}')

        if isinstance(X, pd.DataFrame) and X.shape[1]>1:
            pass

        else:
            X_diff, orders = self._1D_diff(X, precision, method, order)


        if return_order:
            return X_diff, orders

        else return X_diff

