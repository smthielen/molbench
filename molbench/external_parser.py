"""Python file for all external parsers.

"""
import os.path
import molbench.logger as log

class ExternalParser:
    """
    Parent class for an Output-API.

    This class is used to load external data from a directory. Any class that 
    is supposed to load external data from a directory must inherit from this 
    class. The naming convention for subclasses is [SUITE]_[METHOD]_Parser 
    (e. g. PySCF_FCI_Parser, QChem_MP2_Parser, ORCA_CCSDT_Parser).

    Methods
    -------
    load(filepath: str, suffix: str = 'out') -> dict
        Load external data from the specified filepath with the given suffix.

    Attributes
    ----------
    None
    """

    def __init__(self):
        pass

    def load(self, filepath: str, suffix: str = 'out') -> dict:
        return None

    def _fetch_all_outfiles(self, path: str, suffix: str = 'out') -> list:
        outfiles = []

        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(suffix):
                    fp = os.path.abspath(os.path.join(root, f))
                    outfiles.append(fp)

        return outfiles

    def _assign_outfiles_to_benchmark(self, outfiles: list, 
                                      comp_benchmark: dict) -> dict:
        assignment = {}
        for outfile in outfiles:
            for compkey in comp_benchmark:
                if compkey[0] in outfile:
                    assignment[outfile] = compkey
                    break
            if not outfile in assignment:
                # TODO look into file to find assignment or go home and cry
                pass
        return assignment

class QChem_MP2_Parser(ExternalParser):
    
    def __init__(self):
        super().__init__()

    def load(self, filepath: str, suffix: str = 'out') -> dict:
        outfiles = self._fetch_all_outfiles(filepath, suffix)


class PySCF_FCI_Parser(ExternalParser):

    def __init__(self):
        super().__init__()

    def load(self, filepath: str, suffix: str = 'out') -> dict:
        # TODO
        return None


