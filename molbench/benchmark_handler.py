"""Python script for handling benchmarks.


"""

import os
import json
import molbench.logger as log

premade_benchmarks = None


def _collect_premade_benchmarks():
    global premade_benchmarks
    if premade_benchmarks is None:
        return

    wpath = os.path.dirname(os.path.abspath(__file__))
    rpath = os.path.join(wpath, "resources")
    premade_benchmarks = {}
    for root, _, files in os.walk(rpath):
        for file in files:
            if file.endswith('.json'):
                key = os.path.splittext(file)[0]
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
