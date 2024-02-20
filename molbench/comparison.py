"""

Comparison

Structure as follows

molkey -> basis -> method -> property

"""

import molbench.logger as log

class Comparison(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def __setattr__(self, attr: str, val) -> None:
        self[attr] = val

    def init_from_benchmark(self, benchmark: dict) -> None:
        if isinstance(benchmark, Comparison):
            return
        self.clear()
        for molkey, moldict in benchmark.items():
            if not "properties" in moldict:
                continue
            if len(moldict["properties"]) == 0:
                continue
            
            bases_methods = set([(prop['basis'], prop['method']) for prop in 
                                moldict['properties'].values() if 'basis' in 
                                prop and 'method' in prop])
            
            if len(bases_methods) == 0:
                continue
            
            local_dict = {}
            for bm in bases_methods:
                basis, method = bm
                if basis not in local_dict:
                    local_dict[basis] = {}
                if method not in local_dict[basis]:
                    local_dict[basis][method] = {}
            for prop in moldict["properties"]:
                d = local_dict[prop["basis"]][prop["method"]]
                d[prop["type"]] = prop["value"]
            
            self[molkey] = local_dict

    def include_external(self, external: dict, signatures: dict) -> None:
        if set(external.keys()) != set(signatures.keys()):
            log.error("External data and signatures do not match.", self)
            return
        ext_keys = list(external.keys())
        for ext_key in ext_keys:
            method = signatures[ext_key]["method"]
            basis = signatures[ext_key]["basis"]
            molkey = signatures[ext_key]["molkey"]
            if not molkey in self:
                self[molkey] = {}
            if not basis in self[molkey]:
                self[molkey][basis] = {}
            if not method in self[molkey][basis]:
                self[molkey][basis][method] = {}
            self[molkey][basis][method].update(external[ext_key])

class Comparator:
    """
    Parent class for a comparison between external data and a benchmark set.

    This class is used to perform comparisons between external data and a benchmark set. Any class that is supposed to perform such comparisons must inherit from this class.

    Methods
    -------
    compare(benchmark: dict, external_data: dict, properties: tuple) -> str
        Compare benchmark data with external data and return file contents of the comparison.

    Attributes
    ----------
    None
    """

    def __init__(self):
        pass

    def compare(benchmark: dict, external_data: dict, properties: tuple) -> str:
        return None


class CsvComparator(Comparator):

    def __init__(self):
        super().__init__()

    def compare(benchmark: dict, external_data: dict, properties: tuple) -> str:
        # TODO
        return None


