""" Formatting of datapoints """


class Formatter:

    def __init__(self):
        pass

    def format_datapoint(self, dp, proptype):
        return None

class StdFormatter(Formatter):

    def __init__(self):
        super().__init__()

    def format_datapoint(self, dp, proptype):
        if isinstance(dp, str):
            return dp
        if isinstance(dp, (int, float, complex)):
            return str(round(dp, 5))
        if hasattr(dp, '__iter__') or hasattr(dp, '__getitem__'):
            return ", ".join(dp)
