"""Configuration main class.

"""

import os
import json
import molbench.logger as log

config = None


def _init_instance():
    if config is not None:
        return
    instance = Configuration()
    instance.load_from_file()


class Configuration:
    required_fields = {
        "threads": 1,
        "memory": 50000,
        "walltime": "12h"  # XXX: is this valid syntax? nicht eher 12:00:00?
    }

    def __init__(self):
        self.config = {}
        # XXX: alle default werte aus der File sollten direkt geladen werden
        # dann kann man die wenn gewollt überschreiben.
        self.load_from_file()

    def load_from_file(self):
        config_path = os.environ.get("MOLBENCH_CONFIG",
                                     os.path.join(os.path.abspath(__file__),
                                                  "local_configs.json"))
        try:
            with open(config_path, "r") as f:
                self.config = json.load(f)
        except Exception:
            log.critical(f"Configuration file at {config_path} could not be "
                         "parsed.", self)

    def check_required_fields(self):
        if not self.config:
            return

        for field, val in self.required_fields.items():
            if field not in self.config:
                log.warning(f"Expected Configuration value {field} to be set. "
                            f"Reverting to hardcoded standard of {val}",
                            self)
                self.config[field] = val

    def __gettattr__(self, attr: str):
        val = self.config.get(attr, None)
        if val is None:
            raise AttributeError(f"{self} has no attribute {attr}.")
        return val

    def __setattr__(self, attr: str, val) -> None:
        self.config[attr] = val
