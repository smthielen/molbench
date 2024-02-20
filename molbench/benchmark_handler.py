"""Python script for handling benchmarks.


"""

import os
import json
import molbench.logger as log

premade_benchmarks = None


def _collect_premade_benchmarks():
    global premade_benchmarks
    if premade_benchmarks is not None:
        return

    wpath = os.path.dirname(os.path.abspath(__file__))
    rpath = os.path.join(wpath, "benchmarks")
    premade_benchmarks = {}
    for root, _, files in os.walk(rpath):
        for file in files:
            if file.endswith('.json'):
                key = os.path.splitext(file)[0]
                val = os.path.abspath(os.path.join(root, file))
                premade_benchmarks.update({key: val})


def load_benchmark(benchmark: str) -> dict:
    _collect_premade_benchmarks()
    global premade_benchmarks

    # If the benchmark is premade, use the premade benchmark
    # Otherwise, interpret as a path
    if premade_benchmarks is not None and benchmark in premade_benchmarks:
        benchmark = premade_benchmarks[benchmark]
    else:
        if not os.path.exists(benchmark):
            log.critical(f"Benchmark file {benchmark} does not exists or "
                         "cannot be seen.", "load_benchmark")
        if not benchmark.endswith(".json"):
            log.warning(f"Benchmark file {benchmark} is not labelled as JSON. "
                        "Loading may nonetheless be possible.",
                        "load_benchmark")

    try:
        with open(benchmark, "r") as f:
            bm_dict = json.load(f)
    except json.JSONDecodeError:
        log.critical(f"Benchmark file {benchmark} cannot be read.")

    return bm_dict

def convert_to_comparable(benchmark: dict) -> dict:
    comparable = {}
    for molkey, moldict in benchmark.items():
        if not "properties" in moldict:
            continue
        if len(moldict["properties"]) == 0:
            continue
        methods_bases = set([(prop['method'], prop['basis']) for prop in 
                            moldict['properties'].values() if 'basis' in prop 
                            and 'method' in prop])
        for method_basis in methods_bases:
            method, basis = method_basis
            local_props = {}
            for prop in moldict['properties']:
                if (prop['method'], prop['basis']) == method_basis:
                    local_props[prop['type']] = prop['value']
            comparable[(molkey, method, basis)] = local_props
    return comparable
                    



