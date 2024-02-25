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

    def compare(self, interest: dict, reference: dict) -> numpy.ndarray:
        """Compare two datasets and return interest - ref"""
        # Rules for the keys in the description:
        # - keys that appear in both descriptions are clearly defined and
        #   therefore can be clearly mapped onto each other
        # - keys that only appear in one of the descriptions only restrict one
        #   property (basis...) in one of the subsets. Since values can only
        #   be assigned to ref OR interest, this automatically should also
        #   restrict the other space: ref with method = FCI -> all FCI values
        #   will be used as ref therefore not available as interest.
        #  XXX
        #   * For assigning interest vals to ref vals, no restriction should
        #   be applied to the unrestricted subset -> compare the FCI values
        #   with all available other methods.
        #   * This would be the desired variant for method, but for basis sets
        #   it would make more sense to enforce the basis sets to be the same
        #   * Alternatively, one could exclude the specified value in the
        #   other subset which is partially already achieved by assigning
        #   each value to one of the subsets
        #  XXX
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
        #     given once: have to be equal! -> special
        #     not given: have to be equal
        #   * proptype:
        #     given twice: fixed
        #     given_once: have to be equal -> special
        #     not given: have to be equal

        common_keys = interest.keys() & reference.keys()
        fixed_interest_separators = {interest[k] for k in common_keys
                                     if k in interest}
        all_separators = self.data.structure

        def identify(separators) -> str | None:
            local_dict = {k: v for k, v in zip(self.data.structure,
                                               separators)}
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
                # key already fixed or data_id special case
                if sep in fixed_interest_separators or sep == "data_id":
                    separators.append(None)
                # name + property special case or key not given
                # -> have to be equal
                elif sep in ["name", "proptype"] or (sep not in interest and
                                                     sep not in reference):
                    separators.append(ref_sep)
                else:
                    # key only appears once
                    # XXX this currently allows all values
                    separators.append(None)
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

    def _compare(self, identify: callable, get_interest_values: callable):
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

        # XXX: How to store the signed errors? if we don't keep the keys
        #      information is lost... do we want to keep all the information?
        signed_errors = defaultdict(dict)
        for (ref_keys, ref) in reference:
            interest_values = get_interest_values(ref_keys, interest)
            for interest_keys, values in interest_values:
                signed_errors[ref_keys][interest_keys] = values - ref
        return signed_errors

    def evaluate(self, signed_errors: numpy.ndarray):
        pass
