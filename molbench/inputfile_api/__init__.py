import os
import importlib.util

current_directory = os.path.dirname(__file__)

for filename in os.listdir(current_directory):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]  # Remove ".py" extension
        module_path = os.path.join(current_directory, filename)

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
