import csv
from io import BytesIO, StringIO
from zipfile import ZipFile
from ._downloader import DataDownloader

import pandas as pd
import requests

import quantools as qt


class InseeDownloader(DataDownloader):
    """Downloader for the French National Institute of Statistics and Economic Studies (INSEE)."""

    def __init__(self, save_dir: str = "data", **kwargs):
        super().__init__("/".join((save_dir, "insee")), **kwargs)

        if "start_period" not in kwargs:
            self.start_period = 1
        else:
            self.start_period = kwargs["start_period"]

        self.end_period = 12 if "end_period" not in kwargs else kwargs["end_period"]
        self.start_year = 1970 if "start_year" not in kwargs else kwargs["start_year"]
        self.end_year = 2022 if "end_year" not in kwargs else kwargs["end_year"]

    def _build_url_from_kwargs(self) -> str:
        return f'https://www.insee.fr/en/statistiques/serie/telecharger/csv/{self.kwargs["id"]}?ordre=chronologique&transposition=donneescolonne&periodeDebut={self.start_period}&anneeDebut={self.start_year}&periodeFin={self.end_period}&anneeFin={self.end_year}&revision=sansrevisions'

    def _process_data_file(self):
        return self._data

    def _get_data_from_url(self):
        self._data_file = None
        r = requests.get(self.url)
        files = ZipFile(BytesIO(r.content))
        self._data_file = files.open(files.namelist()[0])
        self._data = qt.Table(self._data_file, is_str_data = True, sep=';', header=0, skiprows=[1, 2, 3])
        return self._data


if __name__ == "__main__":
    import os

    print(os.getcwd())
    downloader = InseeDownloader(id="001786251")
    downloader.get()
