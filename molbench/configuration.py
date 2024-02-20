"""Configuration main class.

"""

import os
import json
import molbench.logger as log


class Configuration(dict):
    required_fields = {
        "threads": 1,
        "memory": 50000,
        "walltime": "12:00:00"
    }

    def __init__(self, *args, **kwargs):
        self.load_from_file()
        super().__init__(self, *args, **kwargs)

    def load_from_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        default_config = os.path.join(current_dir, "local_config.json")
        config_path = os.environ.get("MOLBENCH_CONFIG", default_config)
        try:
            with open(config_path, "r") as f:
                self.update(json.load(f))
        except Exception:
            log.critical(f"Configuration file at {config_path} could not be "
                         "parsed.", self)

    def check_required_fields(self):
        for field, val in self.required_fields.items():
            if field not in self:
                log.warning(f"Expected Configuration value {field} to be set. "
                            f"Reverting to hardcoded standard of {val}",
                            self)
                self[field] = val

    def __setattr__(self, attr: str, val) -> None:
        self[attr] = val


config = Configuration()
