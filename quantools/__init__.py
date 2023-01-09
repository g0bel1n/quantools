from .processing.fractionaldiff import FractionalDiff
from .table import Table, TableSeries
from .plotting import plot
from .utils.sample_data import generate_brownian_prices, generate_brownian_returns

from  .downloading import *

import logging
import seaborn as sns

sns.set()

logger = logging.getLogger()  # Logger
logger_handler = logging.StreamHandler()  # Handler for the logger
logger.addHandler(logger_handler)

# First, generic formatter:
logger_handler.setFormatter(logging.Formatter('Quantools : %(message)s'))
logging.basicConfig(level=logging.INFO)

__all__ = ["Table", "TableSeries", "FractionalDiff", "plot", "generate_brownian_prices", "generate_brownian_returns", "downloading"]