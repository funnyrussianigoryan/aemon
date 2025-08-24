from pathlib import Path

import pytest
import yaml

from aemon.config.loader import ConfigLoader
from aemon.core.generator import OpenAPIGenerator


def test_generate_command_creates_openapi_spec(
    temp_dir: Path, 
    test_fastapi_app_file: Path, 
    mock_config_loader
):
    """Тест проверяет, что команда generate создает корректную OpenAPI спецификацию."""
    config = ConfigLoader()
    output_dir = config.get_output_dir()

    generator = OpenAPIGenerator(
        module_path=str(test_fastapi_app_file),
        app_name="app",
        config=config,
    )
    version = generator.generate()
    
    assert version == "v1"
    
    version_dir = output_dir / version
    assert version_dir.exists()
    assert version_dir.is_dir()
    
    spec_file = version_dir / "api_config.yaml"
    assert spec_file.exists()

    with spec_file.open('r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)

    assert spec['info']['title'] == 'Test API'
    assert spec['info']['description'] == 'API for testing aemon'
    assert spec['info']['version'] == '1.0.0'
    
    paths = spec['paths']
    assert '/users/{user_id}' in paths
    assert '/users' in paths
    assert '/items/{item_id}' in paths
    assert '/items' in paths
    
    assert 'get' in paths['/users/{user_id}']
    assert 'post' in paths['/users']
    assert 'get' in paths['/items/{item_id}']
    assert 'post' in paths['/items']


def test_generate_command_with_invalid_module_path(mock_config_loader):
    """Тест проверяет обработку ошибки при неверном пути к модулю."""
    config = ConfigLoader()
    invalid_path = "nonexistent_file.py"
    
    with pytest.raises((ImportError, FileNotFoundError)):
        generator = OpenAPIGenerator(
            module_path=invalid_path,
            app_name="app",
            config=config,
        )
        generator.generate()


def test_generate_command_with_invalid_app_name(
    test_fastapi_app_file: Path, 
    mock_config_loader
):
    """Тест проверяет обработку ошибки при неверном имени приложения."""
    config = ConfigLoader()
    invalid_app_name = "nonexistent_app"
    
    with pytest.raises(ValueError, match="is not instance of FastAPI app"):
        generator = OpenAPIGenerator(
            module_path=str(test_fastapi_app_file),
            app_name=invalid_app_name,
            config=config,
        )
        generator.generate()
