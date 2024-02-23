""" Formatting of datapoints """


class Formatter:

    def __init__(self):
        pass

    def format_datapoint(self, dp, proptype):
        return None


class StdFormatter(Formatter):

    def __init__(self, n_decimals: int = 5) -> None:
        super().__init__()
        self.n_decimals = n_decimals

    def format_datapoint(self, val, proptype):
        if isinstance(val, str):
            return val
        elif isinstance(val, (int, float, complex)):
            return str(round(val, self.n_decimals))
        elif val is None:
            return "None"
        elif hasattr(val, '__iter__'):  # dict, set, list, tuple, ...
            return ", ".join(self.format_datapoint(v, proptype) for v in val)
