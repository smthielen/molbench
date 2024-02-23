""" Formatting of datapoints """


class Formatter:

    def __init__(self):
        pass

    def format_datapoint(self, dp, proptype):
        return None


class StdFormatter(Formatter):

    def __init__(self, n_decimals: int = 5, empty_field: str = "") -> None:
        super().__init__()
        self.n_decimals = n_decimals
        self.empty_field = empty_field

    def format_datapoint(self, val, proptype):
        if isinstance(val, (int, float, complex)):
            return str(round(val, self.n_decimals))
        elif hasattr(val, '__iter__'):  # dict, set, list, tuple, ...
            return ", ".join(self.format_datapoint(v, proptype) for v in val)
        elif val is None:
            return self.empty_field
        else:
            return str(val)
