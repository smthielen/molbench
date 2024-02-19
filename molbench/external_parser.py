"""Python file for all external parsers.

"""

import molbench.logger as log

class ExternalParser:
    """
    Parent class for an Output-API.

    This class is used to load external data from a directory. Any class that is supposed to load external data from a directory must inherit from this class. The naming convention for subclasses is [SUITE]_[METHOD]_Parser (e. g. PySCF_FCI_Parser, QChem_MP2_Parser, ORCA_CCSDT_Parser).

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

    def load(filepath: str, suffix: str = 'out') -> dict:
        return None


class PySCF_FCI_Parser(ExternalParser):

    def __init__(self):
        super().__init__()

    def load(filepath: str, suffix: str = 'out') -> dict:
        # TODO
        return None


