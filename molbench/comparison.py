"""

Comparison

Structure as follows

name -> basis -> method -> property -> id/path

"""

import molbench.logger as log
from .formatter import StdFormatter

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

    def compare(self, comparison: Comparison, properties: tuple) -> str:
        return None

class CsvComparator(Comparator):

    def __init__(self, flatten_visual=False):
        super().__init__()
        self.flatten_visual = flatten_visual

    def build_row_column_label(self, rows, columns, name, basis, method, data_id):
        rl, cl = [], []
        if "name" in rows:
            rl.append(name)
        else:
            cl.append(name)
        if "basis" in rows:
            rl.append(basis)
        else:
            cl.append(basis)
        if "method" in rows:
            rl.append(method)
        else:
            cl.append(method)
        if "data_id" in rows:
            rl.append(data_id)
        else:
            cl.append(data_id)

        return "///".join(rl), "///".join(cl)

    def compare(self, comparison: Comparison, columns: tuple, prop: str, filepath: str, formatter=None, delimiter=";"):
        all_fields = ["name", "basis", "method", "data_id"]
        columns = [s.lower().strip() for s in columns]
        rows = [s for s in all_fields if s not in columns]
        column_labels = set()
        row_labels = set()
        if formatter == None:
            formatter = StdFormatter()

        # Build rows and columns
        for name in comparison:
            for basis in (d := comparison[name]):
                for method in (d :=[basis]):
                    if prop not in d[method]:
                        continue
                    for data_id in (d := d[method]):
                        rl, cl = self.build_row_column_label(rows, columns, name, basis, method, data_id)
                        column_labels.append(cl)
                        row_labels.append(rl)
        column_labels = sorted(list(column_labels))
        row_labels = sorted(list(row_labels))

        data = numpy.zeros((len(row_labels), len(column_labels)), dtype=str)

        for name in comparison:
            for basis in (d := comparison[name]):
                for method in (d := d[basis]):
                    if prop not in d[method]:
                        continue
                    for data_id in (d := d[method]):
                        val = d[data_id]
                        rl, cl = self.build_row_column_label(rows, columns, name, basis, method, data_id)
                        ri = row_labels.index(rl)
                        ci = column_labels.index(cl)
                        data[ri, ci] = formatter.format_datapoint(val, prop)

        csv_list = [delimiter.join([""].extend(column_labels))]
        for i, rl in enumerate(row_labels):
            csv_list.append(rl + delimiter + delimiter.join(data[i]))

        print("\n".join(csv_list))
        quit()

        with open(filepath, "w") as f:
            f.write("\n".join(csv_list))



