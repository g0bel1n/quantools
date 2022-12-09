from .processing.fractionaldiff import FractionalDiff
from .table.table import Table


import logging
import seaborn as sns

sns.set()

logger = logging.getLogger()  # Logger
logger_handler = logging.StreamHandler()  # Handler for the logger
logger.addHandler(logger_handler)

# First, generic formatter:
logger_handler.setFormatter(logging.Formatter('Quantools : %(message)s'))
logging.basicConfig(level=logging.INFO)

__all__ = ["FractionalDiff", "Table"]
