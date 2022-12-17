import pandas as pd
from pandas import DataFrame, Series
import os
import logging
import numpy as np
from typing import Optional, Union
import re

from quantools.processing import FractionalDiff

logger = logging.getLogger(__name__)
authorized_filetype = ["csv", "json", "excel", "txt"]


def return_Table(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return (
            Table(result, verbose=False)
            if isinstance(result, (DataFrame, Series))
            else result
        )

    return wrapper


class Table(DataFrame):
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
            if filetype not in authorized_filetype:
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
                logger.warning("No datetime column found")

    def __type__(self):
        return "Table"

    def __repr__(self):
        return f"Table({super().__repr__()})"

    def __str__(self):
        return f"Table({super().__str__()})"

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    @return_Table
    def stationnarize(
        self,
        precision: float = 0.1,
        method: str = "fixed-window",
        order: Optional[Union[float, int]] = None,
        return_order: bool = False,
        inplace=False,
    ):
        num = self.select_dtypes(include='number')

        frac_diff = FractionalDiff()

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

    @return_Table
    def normalize(self, inplace=False):
        num = self.select_dtypes(include='number')

        if not inplace:
            return (num - num.mean()) / num.std()

        self.is_normalized = True

        self.loc[:, num.columns] = (num - num.mean()) / num.std()
        return None

    @return_Table
    def __get_item__(self, key):
        return self[key]

    @return_Table
    def drop(self, labels=None, axis=0, index=None, columns=None, level=None, inplace=False, errors="raise"):
        super().drop(labels=labels, axis=axis, index=index, columns=columns, level=level, inplace=inplace, errors=errors)
        return self

    @return_Table
    def drop_duplicates(self, subset=..., keep: bool = ..., inplace: bool = ..., ignore_index: bool = ...) -> DataFrame:
        return super().drop_duplicates(subset, keep, inplace, ignore_index)
