"""Enhanced configuration loader supporting multiple formats and validation."""
import json
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from aemon.core.exceptions import ConfigurationError


class ConfigLoader:
    """Enhanced configuration loader with support for multiple formats."""
    
    DEFAULT_CONFIG = {
        "output_dir": "docs/api",
        "title": "API Documentation",
        "description": "Generated API documentation",
        "version_prefix": "v",
        "auto_increment": True,
        "include_schemas": True,
        "swagger_ui_config": {
            "deepLinking": True,
            "displayRequestDuration": True,
            "docExpansion": "none",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
        }
    }
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to configuration file. If None, searches for
                        common config files in current directory.
        """
        self._config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self._config_path = self._find_config_file(config_path)
        
        if self._config_path:
            self._load_config()
        
        self._validate_config()

    def _find_config_file(self, config_path: Optional[Union[str, Path]]) -> Optional[Path]:
        """Find configuration file."""
        if config_path:
            path = Path(config_path)
            if not path.exists():
                raise ConfigurationError(f"Configuration file not found: {config_path}")
            return path
            
        # Search for common config files
        search_files = [
            "aemon.yaml",
            "aemon.yml", 
            "aemon.json",
            "setup.cfg",
            ".aemon.yaml",
            ".aemon.yml",
        ]
        
        for filename in search_files:
            path = Path(filename)
            if path.exists():
                return path
                
        return None

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self._config_path:
            return
            
        try:
            if self._config_path.suffix in ['.yaml', '.yml']:
                self._load_yaml_config()
            elif self._config_path.suffix == '.json':
                self._load_json_config()
            elif self._config_path.suffix == '.cfg':
                self._load_cfg_config()
            else:
                raise ConfigurationError(f"Unsupported config format: {self._config_path.suffix}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {self._config_path}: {e}") from e

    def _load_yaml_config(self) -> None:
        """Load YAML configuration."""
        with self._config_path.open('r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
            
        if 'aemon' in yaml_config:
            self._config.update(yaml_config['aemon'])
        else:
            self._config.update(yaml_config)

    def _load_json_config(self) -> None:
        """Load JSON configuration."""
        with self._config_path.open('r', encoding='utf-8') as f:
            json_config = json.load(f)
            
        if 'aemon' in json_config:
            self._config.update(json_config['aemon'])
        else:
            self._config.update(json_config)

    def _load_cfg_config(self) -> None:
        """Load INI-style configuration."""
        config_parser = ConfigParser()
        config_parser.read(self._config_path)
        
        if 'aemon' in config_parser:
            section = config_parser['aemon']
            for key, value in section.items():
                # Try to parse as JSON for complex values
                try:
                    self._config[key] = json.loads(value)
                except json.JSONDecodeError:
                    # Keep as string
                    self._config[key] = value

    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Validate output directory
        output_dir = self.get_output_dir()
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConfigurationError(f"Cannot create output directory {output_dir}: {e}") from e

    def get_version(self) -> str:
        """Get next version of API spec."""
        if not self._config.get("auto_increment", True):
            return self._config.get("version", "v1")
            
        prefix = self._config.get("version_prefix", "v")
        output_dir = self.get_output_dir()
        
        if not output_dir.exists():
            return f"{prefix}1"
            
        existing = sorted(
            [d.name for d in output_dir.glob(f"{prefix}*") if d.is_dir()],
        )
        
        if not existing:
            return f"{prefix}1"
            
        # Extract version numbers
        version_numbers = []
        for version_dir in existing:
            version_num = version_dir[len(prefix):]
            if version_num.isdigit():
                version_numbers.append(int(version_num))
                
        if not version_numbers:
            return f"{prefix}1"
            
        last_version = max(version_numbers)
        return f"{prefix}{last_version + 1}"

    def get_output_dir(self) -> Path:
        """Get path of docs directory."""
        return Path(self._config.get("output_dir", "docs/api"))

    def get_title(self) -> str:
        """Get documentation title."""
        return self._config.get("title", "API Documentation")

    def get_description(self) -> str:
        """Get documentation description."""
        return self._config.get("description", "Generated API documentation")

    def get_swagger_ui_config(self) -> Dict[str, Any]:
        """Get Swagger UI configuration."""
        return self._config.get("swagger_ui_config", {})

    def should_include_schemas(self) -> bool:
        """Check if schemas should be included in output."""
        return self._config.get("include_schemas", True)

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get any configuration value."""
        return self._config.get(key, default)

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration values."""
        self._config.update(updates)
        self._validate_config()

    def save_config(self, path: Optional[Union[str, Path]] = None) -> None:
        """Save current configuration to file."""
        if not path:
            path = self._config_path or Path("aemon.yaml")
        else:
            path = Path(path)
            
        config_to_save = {"aemon": self._config}
        
        if path.suffix in ['.yaml', '.yml']:
            with path.open('w', encoding='utf-8') as f:
                yaml.dump(config_to_save, f, default_flow_style=False, allow_unicode=True)
        elif path.suffix == '.json':
            with path.open('w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
        else:
            raise ConfigurationError(f"Unsupported config format for saving: {path.suffix}")

    def __repr__(self) -> str:
        """String representation of config."""
        return f"ConfigLoader(config_path={self._config_path}, output_dir={self.get_output_dir()})"
