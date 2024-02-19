"""Python file for input constructors.

"""

import molbench.logger as log

class InputConstructor:
    """
    Parent class for an Inputfile-API.

    This class is used to write input files for a benchmark. Any class that is supposed to write input files for a benchmark must inherit from this class.

    Methods
    -------
    create(benchmark: dict, filepath: str, flat_structure: bool = False, name_template: str = '[[name]]_[[method]]_[[basis]].in') -> None
        Create input files for the given benchmark at the specified filepath.

    Attributes
    ----------
    None
    """

    def __init__(self):
        pass

    def create(benchmark: dict, filepath: str, flat_structure: bool = False, name_template: str = '[[name]]_[[method]]_[[basis]].in'):
        pass

class PySCF_FCI_Constructor(InputConstructor):

    def __init__(self):
        super().__init__()

    def create(benchmark: dict, filepath: str, flat_structure: bool = False, name_template: str = '[[name]]_fci_[[basis]].in'):
        # TODO
        pass


