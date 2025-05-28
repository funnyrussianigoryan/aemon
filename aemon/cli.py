import argparse
import configparser
import importlib.util
import json
import logging
from pathlib import Path


# done
def get_config():
    config = configparser.ConfigParser()
    config.read("setup.cfg")
    return config

# done
def get_output_dir(config):
    return Path(config.get("aemon", "output_dir", fallback="docs/api"))

# done
def determine_next_version(output_dir: Path) -> str:
    existing = sorted([d.name for d in output_dir.glob("v*") if d.is_dir()])
    if not existing:
        return "v1"
    last_version = max(int(d[1:]) for d in existing if d[1:].isdigit())
    return f"v{last_version + 1}"


def load_fastapi_app(module_path: str, app_variable: str = "app"):
    spec = importlib.util.spec_from_file_location("fast_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, app_variable)


def dump_openapi(app, output_dir: Path, version: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    version_dir = output_dir / version
    version_dir.mkdir(exist_ok=True)
    with open(version_dir / "openapi.json", "w", encoding="utf-8") as f:
        json.dump(app.openapi(), f, indent=2, ensure_ascii=False)
    logging.info(f"OpenAPI спецификация сохранена: {version_dir / 'openapi.json'}")


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Сохраняет OpenAPI спецификацию FastAPI-приложения")
    parser.add_argument("--module", "-m", required=True, help="Путь к модулю FastAPI-приложения (например, main.py)")
    parser.add_argument("--app", "-a", default="app", help="Имя переменной FastAPI-приложения (по умолчанию 'app')")
    args = parser.parse_args()

    config = get_config()
    output_dir = get_output_dir(config)
    version = determine_next_version(output_dir)

    app = load_fastapi_app(args.module, args.app)
    dump_openapi(app, output_dir, version)
