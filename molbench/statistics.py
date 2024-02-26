from .comparison import Comparison
from . import logger as log
from collections import defaultdict
import numpy


class Statistics:
    """"""
    def __init__(self, data: Comparison) -> None:
        if not isinstance(data, Comparison):
            log.error("Data for statistics evaluation has to be provided as "
                      f"{Comparison}.", self, TypeError)
        self._data = data

    @property
    def data(self):
        return self._data

    def compare(self, interest: dict, reference: dict) -> dict:
        """Compare two datasets and return interest - ref"""
        # Rules for the keys in the description:
        # - keys that appear in both descriptions are clearly defined and
        #   therefore can be clearly mapped onto each other
        # - keys that only appear in one of the descriptions only restrict one
        #   property (basis...) in one of the subsets. Since values can only
        #   be assigned to ref OR interest, this automatically should also
        #   restrict the other space: ref with method = FCI -> all FCI values
        #   will be used as ref therefore not available as interest.
        #   For assigning interest vals to ref vals, no restriction should
        #   be applied to the unrestricted subset -> compare the FCI values
        #   with all available other methods.
        # - keys that don't appear in either of the dictionaries have to be
        #   equal: if basis is not specified in either description
        #   the basis has to be the same for reference and interest value.
        #   all found basis sets are considered.
        # - special keys for assigning ref and interest values:
        #   * data_id:
        #     given twice: fixed
        #     given once: allow all
        #     not given: allow all -> special
        #   * name:
        #     given twice: fixed
        #     given once: allow all
        #     not given: have to be equal
        #   * proptype:
        #     given twice: fixed
        #     given_once: allow all
        #     not given: have to be equal

        common_keys = interest.keys() & reference.keys()
        fixed_interest_separators = {k: interest[k] for k in common_keys}
        all_separators = self.data.structure

        def identify(separators) -> str | None:
            local_dict = {k: v for k, v in zip(all_separators, separators)}
            if reference.items() <= local_dict.items():
                return "reference"
            elif interest.items() <= local_dict.items():
                return "interest"
            else:
                return None

        def get_interest_values(ref_separators: list,
                                interest_pool: list) -> list:
            separators = []
            for ref_sep, sep in zip(ref_separators, all_separators):
                # key already fixed in the input
                if sep in fixed_interest_separators:
                    separators.append(fixed_interest_separators[sep])
                # data_id special case: if not given twice -> allow all
                # or key given once -> allow all
                elif sep == "data_id" or sep in reference:
                    separators.append(None)
                elif sep in interest:  # defined
                    separators.append(interest[sep])
                else:
                    # key not given -> has to be the same as in reference
                    separators.append(ref_sep)
            # filter out all not compatible values
            interest_values = []
            assigned_interest = []
            for i, (keys, value) in enumerate(interest_pool):
                # check if the keys are compatible with the separators
                compatible = True
                for desired_sep, interest_sep in zip(separators, keys):
                    if desired_sep is not None and desired_sep != interest_sep:
                        compatible = False
                        break
                if compatible:
                    interest_values.append((keys, value))
                    assigned_interest.append(i)
            for i in assigned_interest:
                del interest_pool[i]
            return interest_values

        return self._compare(identify, get_interest_values)

    def _compare(self, identify: callable,
                 get_interest_values: callable) -> dict:
        reference = []
        interest = []
        for keys, value in self.data.walk_values():
            role = identify(keys)
            if role is None:  # neither ref nor interest value
                continue
            elif role[0] == "r":
                reference.append((tuple(keys), value))
            elif role[0] == "i":
                interest.append((tuple(keys), value))
            else:
                log.error(f"Could not assign a role to {keys}.", self,
                          ValueError)

        signed_errors = defaultdict(dict)
        for (ref_keys, ref) in reference:
            interest_values = get_interest_values(ref_keys, interest)
            for interest_keys, values in interest_values:
                signed_errors[ref_keys][interest_keys] = values - ref
        return signed_errors

    def evaluate(self, signed_errors: numpy.ndarray):
        pass
