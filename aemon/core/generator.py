import logging
from pathlib import Path

import yaml
from fastapi import FastAPI

from aemon.config.loader import ConfigLoader
from aemon.core.fast_api_loader import FastAPILoader


class OpenAPIGenerator:
    def __init__(self, module_path: str, app_name: str, config: ConfigLoader):
        self.module_path = module_path
        self.app_name = app_name
        self.config = config

    def generate(self) -> str:
        app = FastAPILoader._load_fastapi_app(
            module_path=self.module_path,
            app_name=self.app_name,
        )
        output_dir = self.config.get_output_dir()
        version = self.config.get_version()
        self._save_spec(app, output_dir / version)
        logging.info(f"OpenAPI {version} successfully saved to {output_dir/version}")
        return version

    def _save_spec(self, app: FastAPI, target_dir: Path):
        """Save OpenAPI spec as YAML file compatible with Swagger UI."""
        target_dir.mkdir(parents=True, exist_ok=True)
        spec = app.openapi()
        spec_path = target_dir / "api_config.yaml"
        with spec_path.open("w", encoding="utf-8") as f:
            yaml.dump(spec, f, allow_unicode=True)
