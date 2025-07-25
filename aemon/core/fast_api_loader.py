import importlib.util

from fastapi import FastAPI


class FastAPILoader:

    @staticmethod
    def _load_fastapi_app(module_path: str, app_name: str) -> FastAPI:
        spec = importlib.util.spec_from_file_location("target_module", module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to import module at path: {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        app = getattr(module, app_name, None)
        if not isinstance(app, FastAPI):
            raise ValueError(f"Variable {app_name} in {module_path} is not instance of FastAPI app")
        return app
