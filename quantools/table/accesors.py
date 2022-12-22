@pd.api.extensions.register_dataframe_accessor("as_returns")
class ReturnsAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        # verify there is a column latitude and a column longitude
        pass

    @property
    def returns(self):
        return self._obj

    @property
    def sharpes(self):
        return self._obj.mean() / self._obj.std()

    @property
    def calmar(self):
        return self._obj.mean() / (self._obj.div(self._obj.cummax()).sub(1)).max()

    

