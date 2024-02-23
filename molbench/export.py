from .comparison import Comparison
from .formatting import StdFormatter
from collections import defaultdict


class Exporter:
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


class CsvExporter(Exporter):

    def __init__(self, flatten_visual=False):
        super().__init__()
        self.flatten_visual = flatten_visual

    def build_row_column_label(self, columns, sep_names, sep_vals, data_id):
        row_l, column_l = [], []
        name, sep_vals = sep_vals[0], sep_vals[1:]
        if "name" in columns:
            column_l.append(name)
        else:
            row_l.append(name)
        for n, val in zip(sep_names, sep_vals):
            if n in columns:
                column_l.append(val)
            else:
                row_l.append(val)
        if "data_id" in columns:
            column_l.append(data_id)
        else:
            row_l.append(data_id)

        return "///".join(row_l), "///".join(column_l)

    def compare(self, comparison: Comparison, columns: tuple, prop: str,
                filepath: str, formatter=None, delimiter=";"):
        columns = [s.lower().strip() for s in columns]
        column_labels = set()
        if formatter is None:
            formatter = StdFormatter()

        data = defaultdict(dict)
        for keys, propdata in comparison.walk_property(prop):
            for data_id, value in propdata.items():
                row_l, column_l = self.build_row_column_label(
                    columns, comparison.data_separators, keys, data_id
                )
                column_labels.add(column_l)
                data[row_l][column_l] = value
        column_labels = sorted(column_labels)

        csv_list = [delimiter.join(["", *column_labels])]
        for row_l, row_data in data.items():
            row = []
            for column_l in column_labels:
                value = row_data.get(column_l, None)
                row.append(formatter.format_datapoint(value, prop))
            csv_list.append(delimiter.join([row_l, *row]))

        print("\n".join(csv_list))
        quit()

        with open(filepath, "w") as f:
            f.write("\n".join(csv_list))
