"""Python file for input constructors.

"""

import os
from . import logger as log
from .configuration import config
from .functions import substitute_template


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

    def __init__(self, template: str):
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

    def create(self, benchmark: dict, basepath: str, calculation_details: dict,
               input_expansion_keys: tuple[str] = ("basis",),
               flat_structure: bool = False,
               name_template: str = None):
        # For each compound iterate over all combinattions of the
        # input_expansion_keys that exist in the benchmark.
        # By default this means iterate over all basis sets for which
        # reference data is available.
        # For each variant, create a file (and folder in deep structure),
        # then insert template
        basepath_abs = os.path.abspath(basepath)
        inputfile_list = []

        if name_template is None:
            # construct a name that ensures that each file has a unique name
            name_template = "[[name]]_[[method]]"
            for key in input_expansion_keys:
                name_template += f"_[[{key}]]"
            name_template += ".in"

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
            if "xyz" in base_details and \
                    not isinstance(base_details["xyz"], str):
                base_details["xyz"] = "\n".join(base_details["xyz"])

            # find all unique combinations of relevant keys present in the
            # benchmark, skipping all entries where at least one key is not
            # defined
            variants = set()
            for prop in moldict["properties"].values():
                var = tuple(
                    (key, prop.get(key, None)) for key in input_expansion_keys
                )
                if any(v is None for _, v in var):
                    continue
                variants.add(var)

            for var in variants:
                log.debug(f"Now handling: {molkey} -> {var}.")
                details = base_details.copy()
                for k, v in var:
                    # inform if conflicting data exists
                    if k in details:
                        log.warning(f"Found conflicting entry for {k}. "
                                    f"Overwriting existing value {details[k]}"
                                    f"with {v}.", TemplateConstructor)
                    details[k] = v

                # this is direct user input -> use whatever we got and
                # silently overwrite if necessary
                details.update(calculation_details)
                # config should only be relevant for backup -> dont overwrite!
                for key, val in config.items():
                    if key not in details:
                        details[key] = val

                inputfile_contents = substitute_template(self.template,
                                                         details)
                inputfile_name = substitute_template(name_template, details)
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
