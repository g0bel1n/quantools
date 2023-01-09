from abc import ABC, abstractmethod

import requests


import logging
import sys 

import os

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)



class DataDownloader(ABC):

    def __init__(self, save_dir: str = 'data'):

        self.save_dir = save_dir


        self._data = None


    @abstractmethod
    def _build_url_from_kwargs(self, **kwargs) -> str:
        pass




    def _get_url_from_kwargs(self, **kwargs):
        if "url" in kwargs:
            return kwargs["url"]

        else :
            return self._build_url_from_kwargs(**kwargs)


    @abstractmethod
    def _process_data_file(self):
        pass

    @abstractmethod
    def _get_data_from_url(self):
        pass

    def save(self, filename=None):
        assert self._data is not None, "You must call get() before saving the data"
        if os.path.exists(self.save_dir) is False:
            os.makedirs(self.save_dir)
        if filename is None:
            filename = self.url.split("/")[-1]
        self._data.to_csv(f"{self.save_dir}/{filename}.csv")

    def get(self, save=False, filename=None, **kwargs):
        self.url = self._get_url_from_kwargs(**kwargs)
        self._get_data_from_url()
        self._process_data_file()

        if save:
            self.save(filename=filename)
        return self._data





