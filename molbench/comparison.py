"""

Comparison

Structure as follows

molkey -> basis -> method -> property -> id/path

"""

import molbench.logger as log


class Comparison(dict):

    def __init__(self):
        # this way we could avoid that some values are passed to the dict
        # upon creation
        super().__init__()

    def add_benchmark(self, benchmark: dict, benchmark_id: str) -> None:
        if isinstance(benchmark, Comparison):
            log.error("Cannot parse a Comparison as a benchmark.")
            return
        for name, moldict in benchmark.items():
            properties = moldict.get("properties", None)
            if not properties:  # key does not exist or prop dict is empty
                continue
            for prop in properties.values():
                basis = prop.get("basis", None)
                method = prop.get("method", None)
                proptype = prop.get("type", None)
                value = prop.get("value", None)
                if basis is None or method is None or proptype is None or \
                        value is None:
                    continue
                if name not in self:
                    self[name] = {}
                if basis not in (d := self[name]):
                    d[basis] = {}
                if method not in (d := d[basis]):
                    d[method] = {}
                if proptype not in (d := d[method]):
                    d[proptype] = {}
                if benchmark_id in (d := d[proptype]):
                    log.warning("Benchmark ID is not unique. Found conflicting"
                                f" entry for {name}, {basis}, {method} and "
                                f"{proptype}. Overwriting the exisiting value",
                                Comparison)
                d[benchmark_id] = value

    def add_external(self, external: dict) -> None:
        if isinstance(benchmark, Comparison):
            log.error("Cannot parse a Comparison as external data.")
            return
        for outfile, metadata in external.items():
            basis = metadata.get("basis", None)
            method = metadata.get("method", None)
            name = metadata.get("name", None)
            data = metadata.get("data", None)
            if basis is None or method is None or name is None or data is None:
                continue
            if name not in self:
                self[name] = {}
            if basis not in (d := self[name]):
                d[basis] = {}
            if method not in (d := d[basis]):
                d[method] = {}
            for proptype, value in data.items():
                if proptype not in d[method]:
                    d[method][proptype] = {}
                if outfile in d[method][proptype]:
                    log.warning("Overwriting already existing value for "
                                f"{name}, {basis}, {method} and {proptype}.",
                                Comparison)
                d[method][proptype][outfile] = value


class Comparator:
    """
    Parent class for a comparison between external data and a benchmark set.

    This class is used to perform comparisons between external data and a
    benchmark set. Any class that is supposed to perform such comparisons must
    inherit from this class.

    Methods
    -------
    compare(benchmark: dict, external_data: dict, properties: tuple) -> str
        Compare benchmark data with external data and return file contents of
        the comparison.

    Attributes
    ----------
    None
    """

    def __init__(self):
        pass

    def compare(benchmark: dict, external_data: dict,
                properties: tuple) -> str:
        return None


class CsvComparator(Comparator):

    def __init__(self):
        super().__init__()

    def compare(benchmark: dict, external_data: dict,
                properties: tuple) -> str:
        # TODO
        return None
