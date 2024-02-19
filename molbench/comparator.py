"""Python file for comparators.


"""

import molbench.logging as log

class Comparator:
    """
    Parent class for a comparison between external data and a benchmark set.

    This class is used to perform comparisons between external data and a benchmark set. Any class that is supposed to perform such comparisons must inherit from this class.

    Methods
    -------
    compare(benchmark: dict, external_data: dict, properties: tuple) -> str
        Compare benchmark data with external data and return file contents of the comparison.

    Attributes
    ----------
    None
    """

    def __init__(self):
        pass

    def compare(benchmark: dict, external_data: dict, properties: tuple) -> str:
        return None


class CsvComparator(Comparator):

    def __init__(self):
        super().__init__()

    def compare(benchmark: dict, external_data: dict, properties: tuple) -> str:
        # TODO
        return None


