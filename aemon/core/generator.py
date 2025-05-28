import importlib.util
import json
import logging
from pathlib import Path

from fastapi import FastAPI

from aemon.config.loader import ConfigLoader


class OpenAPIGenerator:
    def __init__(self, module_path: str, app_name: str, config: ConfigLoader):
        self.module_path = module_path
        self.app_name = app_name
        self.config = config

    def generate(self) -> str:
        app = self._load_fastapi_app()
        output_dir = self.config.get_output_dir()
        version = self.config.get_version()
        self._save_spec(app, output_dir / version)
        logging.info(f"OpenAPI v{version} успешно сохранён")
        return version

    def _load_fastapi_app(self) -> FastAPI:
        spec = importlib.util.spec_from_file_location("target_module", self.module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Не удалось импортировать модуль по пути: {self.module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        app = getattr(module, self.app_name, None)
        if not isinstance(app, FastAPI):
            raise ValueError(f"Объект {self.app_name} в {self.module_path} не является FastAPI-приложением")
        return app

    def _save_spec(self, app: FastAPI, target_dir: Path):
        target_dir.mkdir(parents=True, exist_ok=True)
        spec_path = target_dir / "openapi.json"
        with spec_path.open("w", encoding="utf-8") as f:
            json.dump(app.openapi(), f, indent=2, ensure_ascii=False)