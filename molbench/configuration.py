"""Configuration main class.

"""

import os
import json
import molbench.logger as log

instance = None
hard_defaults = {
"threads": 1,
"memory": 50000,
"walltime": "12h"
        }

def _init_instance():
    if instance is not None:
        return
    instance = Configuration()
    instance.load_from_file()

class Configuration:

    def __init__(self):
        self.config = {}

    def load_from_file(self):
        config_path = os.environ.get("MOLBENCH_CONFIG", os.path.join(os.path.abspath(__file__), "local_configs.json"))
        try:
            with open(config_path, "r") as f:
                self.config = json.load(config_path)
        except Exception:
            log.critical(f"Configuration file at {config_path} could not be parsed.", self)

    def check_expected_fields(self):
        if not self.config:
            return
        global hard_defaults

        for hd, hd_val in hard_defaults.items():
            if hd not in self.config:
                log.warning(f"Expected Configuration value {hd} to be set. Reverting to hardcoded standard of {hd_val}", self)
                self.config[hd] = hd_val

    def get(self, key: str, default=None):
        return self.config.get(key, default)

