# create new pandas dtype for Table
from pandas.api.extensions import ExtensionDtype, register_extension_dtype
import pandas as pd
import numpy as np

from pandas import Float64Dtype


@register_extension_dtype
class Price(Float64Dtype,pd.core.dtypes.dtypes.PandasExtensionDtype):
    name = "Price"
    type = float
    kind = "f"
    na_value = np.nan






@register_extension_dtype
class ReturnPercentage(Float64Dtype):
    """
    Return dtype for pandas

    Returns are defined as the ratio between the current price and the previous price minus 1
    """

    name = "Return"
    type = float
    kind = "f"
    na_value = np.nan


@register_extension_dtype
class ReturnMonetary(Float64Dtype):
    """
    Return dtype for pandas

    Returns are defined as the difference between the current price and the previous price
    """

    name = "Return"
    type = float
    kind = "f"
    na_value = np.nan

    @classmethod
    def construct_from_string(cls, string):
        if string == "Return":
            return cls()
        return super().construct_from_string(string)


@register_extension_dtype
class ReturnLog(Float64Dtype):
    """
    Return dtype for pandas

    Returns are defined as the log of the ratio between the current price and the previous price
    """

    name = "Return"
    type = float
    kind = "f"
    na_value = np.nan


@register_extension_dtype
class Indicator(Float64Dtype):
    """
    Indicator dtype for pandas

    Indicators are defined as number
    """

    name = "Indicator"
    type = float
    kind = "f"
    na_value = np.nan


@register_extension_dtype
class Direction(ExtensionDtype):
    """
    Direction dtype for pandas

    Direction are defined as number
    """

    name = "Direction"
    type = int
    kind = "i"
    na_value = np.nan


@register_extension_dtype
class FractionallyDifferenced(ExtensionDtype):
    """
    Fractionally differenced dtype for pandas

    Fractionally differenced are defined as number
    """

    name = "FractionallyDifferenced"
    type = float
    kind = "f"
    na_value = np.nan


@register_extension_dtype
class Volatility(ExtensionDtype):
    """
    Volatility dtype for pandas

    Volatility are defined as number
    """

    name = "Volatility"
    type = float
    kind = "f"
    na_value = np.nan


@register_extension_dtype
class Position(ExtensionDtype):
    """
    Position dtype for pandas

    Position are defined as number
    """

    name = "Position"
    type = int
    kind = "i"
    na_value = np.nan
