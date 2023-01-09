from abc import ABC, abstractmethod

import requests


import logging
import sys 

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)



class DataDownloader(ABC):

    def __init__(self, save_dir: str = 'data', **kwargs):

        self.save_dir = save_dir

        self.kwargs = kwargs

        self._data = None

        self.url = None


    @abstractmethod
    def _build_url_from_kwargs(self) -> str:
        pass




    def _get_url_from_kwargs(self):
        if "url" in self.kwargs:
            return self.kwargs["url"]

        else :
            return self._build_url_from_kwargs()


    @abstractmethod
    def _process_data_file(self):
        pass

    @abstractmethod
    def _get_data_from_url(self):
        pass

    def get(self):
        self.url = self._get_url_from_kwargs()
        self._get_data_from_url()
        self._process_data_file()
        return self._data





