import os
import importlib.util

"""
This module contains all Scripts that are able to read in Quantum Chemical Outuput files and convert them to MolBench readable format. For this purpose, each file has to follow a specific structure:

For one, a method called parse_output has to be defined which has the following signature:

def parse_output(filecontent: str, method: str, properties: tuple) -> dict:
    (...)

The returned dictionary furthermore is required to have all properties listed in the properties argument as keys and the respective quantities as values.

"""

current_directory = os.path.dirname(__file__)

for filename in os.listdir(current_directory):
    if filename.endswith(".py") and filename != "__init__.py" and filename != "_utils.py":
        module_name = filename[:-3]  # Remove ".py" extension
        module_path = os.path.join(current_directory, filename)

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


