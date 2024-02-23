"""

Comparison

Structure as follows

name -> basis -> method -> property -> id/path

"""

import molbench.logger as log
from .formatting import StdFormatter
from collections import defaultdict

# XXX: Statt filepath filehandler übergeben überall
# -> mehr flexibilität


class Comparison(dict):

    def __init__(self):
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
        if isinstance(external, Comparison):
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

    def compare(self, comparison: Comparison, properties: tuple) -> str:
        return None


class CsvComparator(Comparator):

    def __init__(self, flatten_visual=False):
        super().__init__()
        self.flatten_visual = flatten_visual

    def build_row_column_label(self, columns, name, basis, method, data_id):
        row_l, column_l = [], []
        if "name" in columns:
            column_l.append(name)
        else:
            row_l.append(name)
        if "basis" in columns:
            column_l.append(basis)
        else:
            row_l.append(basis)
        if "method" in columns:
            column_l.append(method)
        else:
            row_l.append(method)
        if "data_id" in columns:
            column_l.append(data_id)
        else:
            row_l.append(data_id)

        return "///".join(row_l), "///".join(column_l)

    def compare(self, comparison: Comparison, columns: tuple, prop: str,
                filepath: str, formatter=None, delimiter=";"):
        columns = [s.lower().strip() for s in columns]
        column_labels = set()
        row_labels = set()
        if formatter is None:
            formatter = StdFormatter()

        data = defaultdict(list)
        column_l = []
        row_l = []
        # Build rows and columns
        for name, moldata in comparison.items():
            for basis, basisdata in moldata.items():
                for method, methoddata in basisdata.items():
                    if prop not in methoddata:
                        continue
                    for data_id, value in methoddata.items():
                        row_l, column_l = self.build_row_column_label(
                            columns, name, basis, method, data_id
                        )
                        column_labels.add(column_l)
                        row_labels.add(row_l)
                        data[(column_l, row_l)].append(value)
        column_labels = sorted(column_labels)
        row_labels = sorted(row_labels)

        # XXX: Gibt es Lücken in den Daten?
        csv_list = [delimiter.join(["", *column_labels])]
        for row_l in row_labels:
            row = []
            for column_l in column_labels:
                value = data.get((column_l, row_l), None)
                row.append(formatter.format_datapoint(value, prop))
            csv_list.append(delimiter.join([row_l, *row]))

        print("\n".join(csv_list))
        quit()

        with open(filepath, "w") as f:
            f.write("\n".join(csv_list))
