"""FastAPI application loader with enhanced error handling and validation."""
import importlib.util
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI

from aemon.core.exceptions import FastAPIAppNotFoundError, InvalidModulePathError


class FastAPILoader:
    """Loader for FastAPI applications with enhanced error handling."""

    @staticmethod
    def load_fastapi_app(module_path: str, app_name: str = "app") -> FastAPI:
        """
        Load FastAPI application from module.
        
        Args:
            module_path: Path to Python module containing FastAPI app
            app_name: Name of FastAPI app variable (default: "app")
            
        Returns:
            FastAPI application instance
            
        Raises:
            InvalidModulePathError: If module cannot be imported
            FastAPIAppNotFoundError: If FastAPI app not found in module
        """
        try:
            return FastAPILoader._load_from_file(module_path, app_name)
        except (ImportError, FileNotFoundError) as e:
            # Try loading as module import path (e.g., "myapp.main")
            try:
                return FastAPILoader._load_from_import_path(module_path, app_name)
            except ImportError:
                raise InvalidModulePathError(
                    f"Failed to import module at path: {module_path}. "
                    f"Original error: {e}"
                ) from e

    @staticmethod
    def _load_from_file(module_path: str, app_name: str) -> FastAPI:
        """Load FastAPI app from file path."""
        path = Path(module_path)
        if not path.exists():
            raise FileNotFoundError(f"Module file not found: {module_path}")
            
        spec = importlib.util.spec_from_file_location("target_module", module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to create module spec for: {module_path}")
            
        module = importlib.util.module_from_spec(spec)
        
        # Add module directory to sys.path temporarily for relative imports
        module_dir = str(path.parent.absolute())
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
            try:
                spec.loader.exec_module(module)
            finally:
                sys.path.remove(module_dir)
        else:
            spec.loader.exec_module(module)
            
        return FastAPILoader._extract_app(module, app_name, module_path)

    @staticmethod
    def _load_from_import_path(import_path: str, app_name: str) -> FastAPI:
        """Load FastAPI app from import path (e.g., 'myapp.main')."""
        try:
            module = importlib.import_module(import_path)
        except ImportError as e:
            raise ImportError(f"Failed to import module: {import_path}") from e
            
        return FastAPILoader._extract_app(module, app_name, import_path)

    @staticmethod
    def _extract_app(module, app_name: str, module_identifier: str) -> FastAPI:
        """Extract FastAPI app from module."""
        app = getattr(module, app_name, None)
        
        if app is None:
            available_attrs = [attr for attr in dir(module) if not attr.startswith('_')]
            raise FastAPIAppNotFoundError(
                f"Variable '{app_name}' not found in {module_identifier}. "
                f"Available attributes: {available_attrs}"
            )
            
        if not isinstance(app, FastAPI):
            raise FastAPIAppNotFoundError(
                f"Variable '{app_name}' in {module_identifier} is not a FastAPI instance. "
                f"Found: {type(app).__name__}"
            )
            
        return app

    @staticmethod
    def validate_app(app: FastAPI) -> Optional[str]:
        """
        Validate FastAPI app and return warnings if any.
        
        Returns:
            Warning message if validation issues found, None otherwise
        """
        warnings = []
        
        # Check if app has routes
        if not app.routes:
            warnings.append("FastAPI app has no routes defined")
            
        # Check if app has title and version
        openapi_schema = app.openapi()
        if not openapi_schema.get("info", {}).get("title"):
            warnings.append("FastAPI app has no title defined")
            
        if not openapi_schema.get("info", {}).get("version"):
            warnings.append("FastAPI app has no version defined")
            
        return "; ".join(warnings) if warnings else None

    # Backward compatibility
    @staticmethod
    def _load_fastapi_app(module_path: str, app_name: str) -> FastAPI:
        """Legacy method for backward compatibility."""
        return FastAPILoader.load_fastapi_app(module_path, app_name)
