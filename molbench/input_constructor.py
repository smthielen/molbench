"""Python file for input constructors.

"""

import os
from . import logger as log
from .configuration import config

class InputConstructor:
    """
    Parent class for an Inputfile-API.

    This class is used to write input files for a benchmark.
    Any class that is supposed to write input files for a benchmark must
    inherit from this class.

    Methods
    -------
    create(benchmark: dict, filepath: str, flat_structure: bool = False,
           name_template: str = '[[name]]_[[method]]_[[basis]].in') -> None
        Create input files for the given benchmark at the specified filepath.

    Attributes
    ----------
    None
    """

    def __init__(self):
        pass

    def create(self, benchmark: dict, filepath: str,
               flat_structure: bool = False,
               name_template: str = '[[name]]_[[method]]_[[basis]].in'
               ) -> list:
        return None


class TemplateConstructor(InputConstructor):
    """
    Constructor that creates input files by substituting from a template.
    """

    def __init__(self, template):
        super().__init__()
        self.init_template(template)

    def init_template(self, template: str):
        wdir = os.path.dirname(os.path.abspath(__file__))
        tdir = os.path.join(wdir, "templates")
        temps = {}

        for root, _, files in os.walk(tdir):
            for f in files:
                if f.endswith(".txt"):
                    fpath = os.path.join(root, f)
                    fname = os.path.splitext(f)[0]
                    temps[fname] = fpath

        if template in temps:
            try:
                with open(temps[template], 'r') as f:
                    self.template = f.read()
            except Exception:
                log.critical(f"Template {template} could not be loaded from "
                             "premade templates.", self)
        else:
            try:
                with open(template, 'r') as f:
                    self.template = f.read()
            except Exception:
                log.critical(f"Custom template {template} could not be "
                             "loaded.", self)

    def _sub_template_vals(self, template: str, subvals: dict) -> str:
        while True:
            start = template.find("[[")
            stop = template.find("]]")
            if start == -1 or stop == -1:
                break
            key = template[start+2:stop]
            val = subvals.get(key, None)
            if val is None:
                log.error(f"No value for required parameter {key} "
                          f"available. Available are {subvals}.", self,
                          KeyError)
            template = template.replace(template[start:stop+2], str(val), 1)
        return template

    def create(self, benchmark: dict, basepath: str, calculation_details: dict,
               flat_structure: bool = False,
               name_template: str = '[[name]]_[[method]]_[[basis]].in'):
        # Iterate over all compounds/basis set combos
        # For each, create a file (and folder in deep structure),
        # then insert template
        basepath_abs = os.path.abspath(basepath)
        inputfile_list = []

        if not os.path.exists(basepath_abs):
            os.makedirs(basepath_abs, exist_ok=True)

        log.info("Path created successfully")

        for molkey, moldict in benchmark.items():
            # Not sure if we want to skip creating input files in this case
            if not moldict.get('properties', {}):
                continue
            base_details = {k: v for k, v in moldict.items()
                            if k != 'properties'}
            if "name" not in base_details:
                base_details["name"] = molkey
            if "xyz" in base_details:
                base_details["xyz"] = "\n".join(base_details["xyz"])

            basis_sets = set([prop['basis'] for prop in 
                              moldict['properties'].values() if 'basis' in prop])
            for basis in basis_sets:
                log.debug(f"Now handling: {molkey} {basis}")
                details = base_details.copy()
                details["basis"] = basis

                details.update(calculation_details)
                for key, val in config.items():
                    if key not in details:
                        details[key] = val

                inputfile_contents = self._sub_template_vals(self.template,
                                                             details)
                inputfile_name = self._sub_template_vals(name_template,
                                                         details)
                if flat_structure:
                    inputfile_path = os.path.join(basepath_abs, inputfile_name)
                else:
                    inputfile_path = os.path.join(basepath_abs, molkey,
                                                  inputfile_name)
                    if not os.path.exists(os.path.join(basepath_abs, molkey)):
                        os.makedirs(os.path.join(basepath_abs, molkey),
                                    exist_ok=True)
                with open(inputfile_path, "w") as f:
                    f.write(inputfile_contents)
                inputfile_list.append(inputfile_path)
        
        return inputfile_list
