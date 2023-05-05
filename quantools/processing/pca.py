import numpy as np

from .dataprocessor import DataProcessor

from quantools.table._table import Table


class PCA(DataProcessor):
    def __init__(self, order: int = 10) -> None:
        super().__init__()
        self.order = order

    def __call__(self, X: Table, **kwargs) -> Table:
        """
        It takes a table and returns the PCA of the table

        :param X: Table
        :type X: Table
        :return: The PCA of the table
        """
        return self._pca(X, self.order)

    def _pca(self, X: Table, order: int) -> Table:
        """
        It takes a table and returns the PCA of the table

        :param X: Table
        :type X: Table
        :return: The PCA of the table
        """

        X_ = X.select_dtypes(include="number")

        order = min(order, X_.shape[1])

        X_ -= X_.mean(axis=0)
        X_ /= X_.std(axis=0)

        cov_mat = X_.cov()

        _, eig_vecs = np.linalg.eigh(cov_mat)  # eig_vecs are already sorted

        columns = [f"PC{i}" for i in range(1, order + 1)]

        return Table(
            (X_ @ eig_vecs[:, -order:]).values,
            columns=columns,
            index=X.index,
            dtype=float,
        )
