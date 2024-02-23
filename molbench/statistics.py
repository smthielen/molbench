from .comparison import Comparison
from . import logger as log
import numpy


class Statistics:
    """"""
    def __init__(self, data: Comparison) -> None:
        self._data = data

    def compare(self, interest: dict, reference: dict) -> numpy.ndarray:
        """Compare two datasets and return interest - ref"""
        def identify_int_ref(values) -> str | None:
            # 1st key = name, last key = data_id
            keys = ["name", *self._data.data_separators, "data_id"]
            local_dict = {k: v for k, v in zip(keys, values)}
            if reference.items() <= local_dict.items():
                return "ref"
            elif interest.items() <= local_dict.items():
                return "int"
            else:
                return None
        return self._compare(identify_int_ref)

    def _compare(self, identify: callable):
        reference = {}
        interest = {}
        for keys, value in self._data.walk_values():
            role = identify(keys)
            if role is None:
                continue
            if hasattr(value, '__iter__'):
                value = numpy.array(value)

            if role == "ref":
                reference[tuple(keys)] = value
            elif role == "int":
                interest[tuple(keys)] = value
            else:
                log.error(f"Could not assign {keys} to reference or interest",
                          self, ValueError)
        signed_errors = []
        for key, ref in reference.items():
            val = interest.get(key)
            if val is None:
                log.debug(f"Could not find value for {key} in interest.")
                continue
            signed_errors.append(val - ref)
        return numpy.array(signed_errors)

    def evaluate(self, signed_errors: numpy.ndarray):
        pass
