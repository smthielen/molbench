"""Python file for all external parsers.

"""
import os.path
import numpy
from . import convert_to_comparable
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

    def load(self, filepath: str, suffix: str = 'out') -> dict, dict:
        return None, None

    def _fetch_all_outfiles(self, path: str, suffix: str = 'out') -> list:
        outfiles = []

        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(suffix):
                    fp = os.path.abspath(os.path.join(root, f))
                    outfiles.append(fp)

        return outfiles


class QChem_MP2_Parser(ExternalParser):
    
    def __init__(self):
        super().__init__()

    def parse_file(self, filename: str, lines: list) -> dict, dict:
        # Signature must contain molkey, basis, method
        signature = {"molkey": filename.split("_")[0]}
        fdict = {}
        # Flags
        dip_flag = False
        mulliken_flag = False
        mul_charges = []

        for line in lines:
            if line.strip() == "":
                continue
            lsplit = line.strip().split()
            lnw = " ".join(lsplit)
            if "basis" not in signature:
                if len(lsplit) >= 2 and lsplit[0].lower() == "basis":
                    b = lsplit[1]
                    if lsplit[1] == "=":
                        b = lsplit[2]
                    signature["basis"] = b
            if "method" not in signature:
                if len(lsplit) >= 2 and lsplit[0].lower() == "method":
                    m = lsplit[1]
                    if lsplit[1] == "=":
                        m = lsplit[2]
                    signature["method"] = m
            if "energy" not in fdict:
                if "MP2 total energy =" in lnw:
                    fdict["energy"] = float(lsplit[-2])
            if "dipole moment" not in fdict:
                if not dip_flag and "Dipole Moment (Debye)" in lnw:
                    dip_flag = True
                    continue
                elif dip_flag:
                    dx, dy, dz = lsplit[1], lsplit[3], lsplit[5]
                    dip_mom = numpy.array([float(dx), float(dy), float(dz)])
                    # Debye to au
                    dip_mom /= 0.393430307
                    fdict["dipole moment"] = tuple(dip_mom)
                    fdict["total dipole moment"] = numpy.linalg.norm(dip_mom)
            if "mulliken charges" not in fdict:
                if "Ground-State Mulliken Net Atomic Charges" in lnw and not mulliken_flag:
                    mulliken_flag = True
                elif mulliken_flag:
                    if lsplit[0] == "Atom":
                        continue
                    if "------------------------" in lsplit[0] and len(mul_charges) == 0:
                        continue
                    if "------------------------" in lsplit[0] and len(mul_charges) > 0:
                        fdict["mulliken charges"] = tuple(mul_charges)
                    else:
                        mul_charges.append(float(lsplit[-1]))

        return fdict, signature

    def load(self, filepath: str, suffix: str = 'out') -> dict, dict:
        outfiles = self._fetch_all_outfiles(filepath, suffix)
        ext_dict = {}
        signatures = {}

        for outfile in outfiles:
            fc = None
            with open(outfile, "r") as f:
                fc = f.readlines()
            ext_dict[outfile], signatures[outfile] = self.parse_file(fc)

        return ext_dict


class PySCF_FCI_Parser(ExternalParser):

    def __init__(self):
        super().__init__()

    def load(self, filepath: str, suffix: str = 'out') -> dict, dict:
        # TODO
        return None


