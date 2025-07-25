"""Comprehensive tests for enhanced aemon functionality."""
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml
from fastapi import FastAPI

from aemon.config.loader import ConfigLoader
from aemon.core.exceptions import (
    AemonError,
    ConfigurationError,
    FastAPIAppNotFoundError,
    InvalidModulePathError,
)
from aemon.core.fast_api_loader import FastAPILoader
from aemon.core.generator import OpenAPIGenerator
from aemon.output.html_generator import HTMLGenerator


class TestConfigLoader:
    """Test configuration loading functionality."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ConfigLoader()
        
        assert config.get_output_dir() == Path("docs/api")
        assert config.get_title() == "API Documentation"
        assert config.get_description() == "Generated API documentation"
        assert config.get_version() == "v1"
        assert config.should_include_schemas() is True
    
    def test_yaml_config_loading(self):
        """Test YAML configuration loading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'aemon': {
                    'output_dir': 'custom/docs',
                    'title': 'Custom API',
                    'version_prefix': 'version',
                }
            }, f)
            config_path = f.name
        
        try:
            config = ConfigLoader(config_path)
            assert config.get_output_dir() == Path("custom/docs")
            assert config.get_title() == "Custom API"
            assert config.get_config_value("version_prefix") == "version"
        finally:
            Path(config_path).unlink()
    
    def test_json_config_loading(self):
        """Test JSON configuration loading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                'aemon': {
                    'output_dir': 'json/docs',
                    'title': 'JSON API',
                }
            }, f)
            config_path = f.name
        
        try:
            config = ConfigLoader(config_path)
            assert config.get_output_dir() == Path("json/docs")
            assert config.get_title() == "JSON API"
        finally:
            Path(config_path).unlink()
    
    def test_invalid_config_file(self):
        """Test handling of invalid configuration file."""
        with pytest.raises(ConfigurationError):
            ConfigLoader("nonexistent.yaml")
    
    def test_version_increment(self):
        """Test version auto-increment functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "docs/api"
            
            # Create existing versions
            (output_dir / "v1").mkdir(parents=True)
            (output_dir / "v2").mkdir(parents=True)
            (output_dir / "v5").mkdir(parents=True)  # Non-sequential
            
            config = ConfigLoader()
            config.update_config({"output_dir": str(output_dir)})
            
            # Should return v6 (max + 1)
            assert config.get_version() == "v6"


class TestFastAPILoader:
    """Test FastAPI application loading."""
    
    def test_load_valid_app(self):
        """Test loading a valid FastAPI application."""
        # Create a temporary FastAPI module
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
from fastapi import FastAPI

app = FastAPI(title="Test API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Hello World"}
""")
            module_path = f.name
        
        try:
            app = FastAPILoader.load_fastapi_app(module_path, "app")
            assert isinstance(app, FastAPI)
            assert app.title == "Test API"
            assert app.version == "1.0.0"
        finally:
            Path(module_path).unlink()
    
    def test_load_app_with_custom_name(self):
        """Test loading FastAPI app with custom variable name."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
from fastapi import FastAPI

api = FastAPI(title="Custom API")
""")
            module_path = f.name
        
        try:
            app = FastAPILoader.load_fastapi_app(module_path, "api")
            assert isinstance(app, FastAPI)
            assert app.title == "Custom API"
        finally:
            Path(module_path).unlink()
    
    def test_app_not_found_error(self):
        """Test error when FastAPI app variable not found."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Empty module")
            module_path = f.name
        
        try:
            with pytest.raises(FastAPIAppNotFoundError) as exc_info:
                FastAPILoader.load_fastapi_app(module_path, "app")
            
            assert "not found" in str(exc_info.value)
        finally:
            Path(module_path).unlink()
    
    def test_invalid_app_type_error(self):
        """Test error when variable is not FastAPI instance."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("app = 'not a fastapi app'")
            module_path = f.name
        
        try:
            with pytest.raises(FastAPIAppNotFoundError) as exc_info:
                FastAPILoader.load_fastapi_app(module_path, "app")
            
            assert "not a FastAPI instance" in str(exc_info.value)
        finally:
            Path(module_path).unlink()
    
    def test_invalid_module_path(self):
        """Test error with invalid module path."""
        with pytest.raises(InvalidModulePathError):
            FastAPILoader.load_fastapi_app("nonexistent.py", "app")
    
    def test_app_validation(self):
        """Test FastAPI app validation."""
        # App with no routes
        empty_app = FastAPI()
        warnings = FastAPILoader.validate_app(empty_app)
        assert "no routes" in warnings.lower()
        
        # App with routes
        app_with_routes = FastAPI(title="Test API", version="1.0.0")
        app_with_routes.get("/")(lambda: {"message": "test"})
        warnings = FastAPILoader.validate_app(app_with_routes)
        assert warnings is None


class TestOpenAPIGenerator:
    """Test OpenAPI generation functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ConfigLoader()
        self.config.update_config({"output_dir": f"{self.temp_dir}/docs/api"})
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_spec(self):
        """Test OpenAPI spec generation."""
        # Create test FastAPI module
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
from fastapi import FastAPI

app = FastAPI(title="Test API", version="1.0.0")

@app.get("/test")
def test_endpoint():
    return {"message": "test"}
""")
            module_path = f.name
        
        try:
            generator = OpenAPIGenerator(module_path, "app", self.config)
            version = generator.generate()
            
            assert version == "v1"
            
            # Check if files were created
            version_dir = self.config.get_output_dir() / version
            assert (version_dir / "api_config.yaml").exists()
            assert (version_dir / "api_config.json").exists()
            assert (version_dir / "metadata.json").exists()
            
            # Check metadata
            with open(version_dir / "metadata.json") as f:
                metadata = json.load(f)
            
            assert metadata["module_path"] == module_path
            assert metadata["app_name"] == "app"
            assert "generated_at" in metadata
            
        finally:
            Path(module_path).unlink()
    
    def test_force_regeneration(self):
        """Test force regeneration of existing spec."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
from fastapi import FastAPI
app = FastAPI(title="Test API")
""")
            module_path = f.name
        
        try:
            generator = OpenAPIGenerator(module_path, "app", self.config)
            
            # Generate first time
            version1 = generator.generate()
            
            # Generate again without force (should skip)
            version2 = generator.generate(force_regenerate=False)
            assert version1 == version2
            
            # Generate with force (should regenerate)
            version3 = generator.generate(force_regenerate=True)
            assert version3 == version1  # Same version but regenerated
            
        finally:
            Path(module_path).unlink()
    
    def test_spec_validation(self):
        """Test OpenAPI spec validation."""
        # Create a valid spec file
        version_dir = self.config.get_output_dir() / "v1"
        version_dir.mkdir(parents=True)
        
        valid_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {"/test": {"get": {"responses": {"200": {"description": "OK"}}}}}
        }
        
        with open(version_dir / "api_config.yaml", 'w') as f:
            yaml.dump(valid_spec, f)
        
        generator = OpenAPIGenerator("", "", self.config)
        result = generator.validate_spec("v1")
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_get_existing_versions(self):
        """Test getting list of existing versions."""
        output_dir = self.config.get_output_dir()
        
        # Create some version directories with specs
        for version in ["v1", "v2", "v3"]:
            version_dir = output_dir / version
            version_dir.mkdir(parents=True)
            (version_dir / "api_config.yaml").write_text("test")
        
        generator = OpenAPIGenerator("", "", self.config)
        versions = generator.get_existing_versions()
        
        assert versions == ["v1", "v2", "v3"]


class TestHTMLGenerator:
    """Test HTML generation functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "docs/api"
        self.config = {"title": "Test API", "description": "Test description"}
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('aemon.output.html_generator.shutil.copytree')
    def test_ensure_assets(self, mock_copytree):
        """Test asset copying."""
        generator = HTMLGenerator(self.output_dir, self.config)
        generator.ensure_assets()
        
        mock_copytree.assert_called_once()
    
    def test_generate_version_page(self):
        """Test version page generation."""
        generator = HTMLGenerator(self.output_dir, self.config)
        version_dir = self.output_dir / "v1"
        
        generator.generate_version_page(version_dir)
        
        assert (version_dir / "index.html").exists()
        
        # Check content
        content = (version_dir / "index.html").read_text()
        assert "API v1" in content
        assert "swagger-ui" in content
        assert "api_config.yaml" in content
    
    def test_generate_html_index_empty(self):
        """Test HTML index generation with no versions."""
        generator = HTMLGenerator(self.output_dir, self.config)
        
        with patch.object(generator, 'ensure_assets'):
            generator.generate_html_index()
        
        index_path = self.output_dir.parent / "index.html"
        assert index_path.exists()
        
        content = index_path.read_text()
        assert "Test API" in content
        assert "No API versions found" in content
    
    def test_generate_html_index_with_versions(self):
        """Test HTML index generation with versions."""
        # Create version directories with metadata
        for i, version in enumerate(["v1", "v2"], 1):
            version_dir = self.output_dir / version
            version_dir.mkdir(parents=True)
            
            metadata = {
                "generated_at": f"2024-01-0{i}T10:00:00",
                "routes_count": i * 5,
                "module_path": f"app{i}.py"
            }
            
            with open(version_dir / "metadata.json", 'w') as f:
                json.dump(metadata, f)
        
        generator = HTMLGenerator(self.output_dir, self.config)
        
        with patch.object(generator, 'ensure_assets'):
            generator.generate_html_index()
        
        index_path = self.output_dir.parent / "index.html"
        content = index_path.read_text()
        
        assert "v1" in content
        assert "v2" in content
        assert "2024-01-01" in content
        assert "2024-01-02" in content


class TestCLIIntegration:
    """Test CLI integration and commands."""
    
    def test_generate_command_args(self):
        """Test generate command argument parsing."""
        from aemon.parser.dto import GenerateCommandArgs
        
        args = GenerateCommandArgs(
            command="generate",
            module="main.py",
            app="api",
            force=True,
            validate=False,
            config="custom.yaml",
            verbose=True
        )
        
        assert args.command == "generate"
        assert args.module == "main.py"
        assert args.app == "api"
        assert args.force is True
        assert args.validate is False
        assert args.config == "custom.yaml"
        assert args.verbose is True
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test AemonError base class
        with pytest.raises(AemonError):
            raise AemonError("Test error")
        
        # Test specific exceptions
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config error")
        
        with pytest.raises(FastAPIAppNotFoundError):
            raise FastAPIAppNotFoundError("App not found")
        
        with pytest.raises(InvalidModulePathError):
            raise InvalidModulePathError("Invalid path")


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    def test_complete_documentation_generation(self):
        """Test complete documentation generation workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test FastAPI app
            app_file = Path(temp_dir) / "test_app.py"
            app_file.write_text("""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="E2E Test API",
    description="End-to-end test API",
    version="1.0.0"
)

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/items/")
def create_item(item: Item):
    return {"item": item}
""")
            
            # Setup configuration
            config = ConfigLoader()
            config.update_config({"output_dir": f"{temp_dir}/docs/api"})
            
            # Generate documentation
            generator = OpenAPIGenerator(str(app_file), "app", config)
            version = generator.generate()
            
            # Generate HTML
            html_generator = HTMLGenerator(
                config.get_output_dir(),
                config._config
            )
            
            with patch.object(html_generator, 'ensure_assets'):
                html_generator.update_index(version)
            
            # Verify output structure
            docs_dir = Path(temp_dir) / "docs"
            assert (docs_dir / "index.html").exists()
            
            version_dir = docs_dir / "api" / version
            assert (version_dir / "index.html").exists()
            assert (version_dir / "api_config.yaml").exists()
            assert (version_dir / "api_config.json").exists()
            assert (version_dir / "metadata.json").exists()
            
            # Verify spec content
            with open(version_dir / "api_config.yaml") as f:
                spec = yaml.safe_load(f)
            
            assert spec["info"]["title"] == "E2E Test API"
            assert spec["info"]["version"] == "1.0.0"
            assert "/items/{item_id}" in spec["paths"]
            assert "/items/" in spec["paths"]
            
            # Verify metadata
            with open(version_dir / "metadata.json") as f:
                metadata = json.load(f)
            
            assert metadata["module_path"] == str(app_file)
            assert metadata["app_name"] == "app"
            assert metadata["routes_count"] >= 3  # At least 3 routes
            
            # Test validation
            validation_result = generator.validate_spec(version)
            assert validation_result["valid"] is True