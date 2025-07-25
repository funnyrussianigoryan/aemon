"""Enhanced OpenAPI generator with validation, caching and error handling."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

import yaml
from fastapi import FastAPI

from aemon.config.loader import ConfigLoader
from aemon.core.fast_api_loader import FastAPILoader
from aemon.core.exceptions import GenerationError


class OpenAPIGenerator:
    """Enhanced OpenAPI generator with validation and caching."""
    
    def __init__(self, module_path: str, app_name: str, config: ConfigLoader):
        """
        Initialize OpenAPI generator.
        
        Args:
            module_path: Path to FastAPI module
            app_name: Name of FastAPI app variable
            config: Configuration loader instance
        """
        self.module_path = module_path
        self.app_name = app_name
        self.config = config
        self.logger = logging.getLogger(__name__)

    def generate(self, force_regenerate: bool = False) -> str:
        """
        Generate OpenAPI specification.
        
        Args:
            force_regenerate: Force regeneration even if spec already exists
            
        Returns:
            Generated version string
            
        Raises:
            GenerationError: If generation fails
        """
        try:
            # Load FastAPI app
            app = FastAPILoader.load_fastapi_app(
                module_path=self.module_path,
                app_name=self.app_name,
            )
            
            # Validate app
            warnings = FastAPILoader.validate_app(app)
            if warnings:
                self.logger.warning(f"FastAPI app validation warnings: {warnings}")
            
            # Determine version and output directory
            version = self.config.get_version()
            output_dir = self.config.get_output_dir()
            version_dir = output_dir / version
            
            # Check if already exists and not forcing regeneration
            if not force_regenerate and self._spec_exists(version_dir):
                self.logger.info(f"OpenAPI spec {version} already exists, skipping generation")
                return version
            
            # Generate and save spec
            self._save_spec(app, version_dir)
            
            # Save metadata
            self._save_metadata(app, version_dir)
            
            self.logger.info(f"OpenAPI {version} successfully generated at {version_dir}")
            return version
            
        except Exception as e:
            raise GenerationError(f"Failed to generate OpenAPI spec: {e}") from e

    def _spec_exists(self, version_dir: Path) -> bool:
        """Check if OpenAPI spec already exists."""
        spec_file = version_dir / "api_config.yaml"
        return spec_file.exists()

    def _save_spec(self, app: FastAPI, target_dir: Path) -> None:
        """Save OpenAPI spec as YAML file compatible with Swagger UI."""
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Get OpenAPI spec
        spec = app.openapi()
        
        # Enhance spec with configuration
        self._enhance_spec(spec)
        
        # Save as YAML
        spec_path = target_dir / "api_config.yaml"
        with spec_path.open("w", encoding="utf-8") as f:
            yaml.dump(spec, f, allow_unicode=True, default_flow_style=False, indent=2)
        
        # Also save as JSON for compatibility
        json_path = target_dir / "api_config.json"
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
        
        self.logger.debug(f"Saved OpenAPI spec to {spec_path} and {json_path}")

    def _enhance_spec(self, spec: Dict[str, Any]) -> None:
        """Enhance OpenAPI spec with additional metadata."""
        # Update info section
        info = spec.setdefault("info", {})
        
        # Set title and description from config if not present
        if not info.get("title"):
            info["title"] = self.config.get_title()
            
        if not info.get("description"):
            info["description"] = self.config.get_description()
        
        # Add generation metadata
        info["x-generated-by"] = "aemon"
        info["x-generated-at"] = datetime.now().isoformat()
        
        # Add contact info if configured
        contact_info = self.config.get_config_value("contact")
        if contact_info:
            info["contact"] = contact_info
            
        # Add license info if configured
        license_info = self.config.get_config_value("license")
        if license_info:
            info["license"] = license_info
        
        # Add servers if configured
        servers = self.config.get_config_value("servers")
        if servers:
            spec["servers"] = servers

    def _save_metadata(self, app: FastAPI, target_dir: Path) -> None:
        """Save generation metadata."""
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "generator": "aemon",
            "module_path": self.module_path,
            "app_name": self.app_name,
            "fastapi_version": getattr(app, "__version__", "unknown"),
            "routes_count": len(app.routes),
            "config": {
                "output_dir": str(self.config.get_output_dir()),
                "title": self.config.get_title(),
                "description": self.config.get_description(),
            }
        }
        
        metadata_path = target_dir / "metadata.json"
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def get_existing_versions(self) -> list[str]:
        """Get list of existing API versions."""
        output_dir = self.config.get_output_dir()
        if not output_dir.exists():
            return []
            
        prefix = self.config.get_config_value("version_prefix", "v")
        versions = []
        
        for version_dir in output_dir.glob(f"{prefix}*"):
            if version_dir.is_dir() and self._spec_exists(version_dir):
                versions.append(version_dir.name)
                
        # Sort versions naturally
        return sorted(versions, key=lambda v: int(v[len(prefix):]) if v[len(prefix):].isdigit() else 0)

    def get_spec_info(self, version: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific API version."""
        version_dir = self.config.get_output_dir() / version
        metadata_path = version_dir / "metadata.json"
        
        if not metadata_path.exists():
            return None
            
        try:
            with metadata_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load metadata for {version}: {e}")
            return None

    def validate_spec(self, version: str) -> Dict[str, Any]:
        """
        Validate OpenAPI specification.
        
        Returns:
            Validation results with errors and warnings
        """
        version_dir = self.config.get_output_dir() / version
        spec_path = version_dir / "api_config.yaml"
        
        if not spec_path.exists():
            return {"valid": False, "errors": [f"Spec file not found: {spec_path}"]}
        
        try:
            with spec_path.open("r", encoding="utf-8") as f:
                spec = yaml.safe_load(f)
        except Exception as e:
            return {"valid": False, "errors": [f"Failed to parse spec: {e}"]}
        
        errors = []
        warnings = []
        
        # Basic validation
        if not spec.get("openapi"):
            errors.append("Missing OpenAPI version")
            
        info = spec.get("info", {})
        if not info.get("title"):
            warnings.append("Missing API title")
        if not info.get("version"):
            warnings.append("Missing API version")
            
        if not spec.get("paths"):
            warnings.append("No API paths defined")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "spec": spec
        }
