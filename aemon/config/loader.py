from configparser import ConfigParser
from pathlib import Path


class ConfigLoader:
    
    def __init__(self):
        self._config = ConfigParser()
        self._config.read('setup.cfg')


    def get_version(self) -> str:
        """Get last version of API spec."""
        existing = sorted(
            [d.name for d in self.get_output_dir().glob("v*") if d.is_dir()],
        )
        if not existing:
            return "v1"
        last_version = max(int(d[1:]) for d in existing if d[1:].isdigit())
        return f"v{last_version + 1}"


    def get_output_dir(self) -> Path:
        """Get path of docs dir."""
        return Path(self._config.get(
            section="aemon",
            option="output_dir",
            fallback="docs/api",
            )
        )
