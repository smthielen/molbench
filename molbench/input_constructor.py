"""Python file for input constructors.

"""

import os
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

    def create(self, benchmark: dict, filepath: str, flat_structure: bool = False, name_template: str = '[[name]]_[[method]]_[[basis]].in'):
        pass

class TemplateConstructor(InputConstructor):
    """
    Constructor that creates input files by substituting from a template.
    """


    def __init__(self, template):
        super().__init__()
        self.template = self.init_template(template)

    def init_template(self, template: str):
        wdir = os.path.dirname(os.path.abspath(__file__))
        tdir = os.path.join(wdir, "templates")
        temps = {}

        for root, dirs, files in os.walk(tdir):
            for f in files:
                if f.endswith(".txt") and "_" in f:
                    fpath = os.path.join(root, f)
                    fname = os.path.splitext(f)[0]
                    temps[fname] = os.path.abspath(fname)
        
        if template in temps:
            try:
                with open(temps[template], 'r') as f:
                    self.template = f.read()
            except Exception:
                log.critical(f"Tempate {template} could not be loaded from premade templates.", self)
        else:
            try: 
                with open(template, 'r') as f:
                    self.template = f.read()
            except Exception:
                log.critical(f"Custom template {template} could not be loaded.", self)


    def _sub_template_vals(self, template: str, subvals: dict) -> str:
        subst = str(template)
        for key, subval in subvals.items():
            subst = subst.replace(f"[[{key}]]", str(subval))
        return subst

    def _check_calc_details_sanity(self, cd: dict) -> dict:
        required_fields = ['method', 'basis']
        fallback_fields = ['threads', 'memory', 'walltime']
        optional_fields = ['kwargs']

        for rq in required_fields:
            if rq not in cd:
                log.error(f"Required field {rq} not found in calculation details. Input files are propably buggy.", self)
                cd.update({rq: ""})
        for ff in fallback_fields:
            if ff not in cd:
                log.warning(f"Field {ff} not found in calculation details. Reverting to global configuration fallback.", self)
                fb_val = molbench.get_config(ff, default="")
                cd.update({ff: fb_val})
        for of in optional_fields:
            if of not in cd:
                cd.update({of: ""})

        return cd

    def create(self, benchmark: dict, basepath: str, calculation_details: dict, flat_structure: bool = False, name_template: str = '[[name]]_[[method]]_[[basis]].in'):
        # Iterate over all compounds/basis set combos
        # For each, create a file (and folder in deep structure), then insert template
        basepath_abs = os.path.abspath(basepath)

        if not os.path.exists(basepath_abs):
            os.makedirs(basepath_abs, exist_ok=True)

        calc_details = self._check_calc_details_sanity(calculation_details)

        for molkey, moldict in benchmark.items():
            if len(moldict.get('properties', {})) == 0:
                continue
            basis_sets = set([prop['basis'] for prop in moldict['properties']])
            for basis in basis_sets:
                details = {"name": molkey, "basis": basis, "xyz": moldict['xyz'], "charge": moldict['charge'], "multiplicity": moldict["multiplicity"]}
                details.update(calc_details)
                inputfile_contents = self._sub_template_vals(self.template, details)
                inputfile_name = self._sub_template_vals(name_template, details)
                if flat_structure:
                    inputfile_path = os.path.join(basepath_abs, inputfile_name)
                else:
                    inputfile_path = os.path.join(basepath_abs, molkey, inputfile_name)
                    if not os.path.exists(os.path.join(basepath_abs, molkey)):
                        os.makedirs(os.path.join(basepath_abs, molkey), exist_ok=True)
                with open(inputfile_path, "w") as f:
                    f.write(inputfile_contents)


