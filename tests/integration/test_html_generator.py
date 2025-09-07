from pathlib import Path

import pytest
import yaml

from aemon.output.html_generator import HTMLGenerator


def test_html_generator_creates_index_page(temp_dir: Path):
    """Тест проверяет, что HTMLGenerator создает индексную страницу со списком версий."""
    docs_dir = temp_dir / "docs"
    api_dir = docs_dir / "api"
    
    for version in ["v1", "v2", "v3"]:
        version_dir = api_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        spec_content = {
            "openapi": "3.1.0",
            "info": {
                "title": f"Test API {version}",
                "version": "1.0.0"
            },
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint"
                    }
                }
            }
        }
        
        spec_file = version_dir / "api_config.yaml"
        with spec_file.open('w', encoding='utf-8') as f:
            yaml.dump(spec_content, f, allow_unicode=True)
    
    html_generator = HTMLGenerator(api_dir)
    
    for version in ["v1", "v2", "v3"]:
        html_generator.update_index(version)
    
    index_file = docs_dir / "index.html"
    assert index_file.exists()
    
    index_content = index_file.read_text(encoding='utf-8')
    assert "API versions list" in index_content
    assert "<table>" in index_content
    assert "api/v1/index.html" in index_content
    assert "api/v2/index.html" in index_content
    assert "api/v3/index.html" in index_content


def test_html_generator_update_with_new_version(temp_dir: Path):
    """Тест проверяет обновление HTML при добавлении новой версии."""
    # Arrange
    docs_dir = temp_dir / "docs"
    api_dir = docs_dir / "api"
    
    # Создаем существующие версии
    for version in ["v1", "v2"]:
        version_dir = api_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        spec_file = version_dir / "api_config.yaml"
        spec_file.write_text("openapi: '3.1.0'\ninfo:\n  title: Test API\n  version: '1.0.0'\npaths: {}")
    
    html_generator = HTMLGenerator(api_dir)
    html_generator.update_index()
    
    # Проверяем начальное состояние
    index_file = docs_dir / "index.html"
    initial_content = index_file.read_text(encoding='utf-8')
    assert "api/v1/index.html" in initial_content
    assert "api/v2/index.html" in initial_content
    assert "api/v3/index.html" not in initial_content
    
    # Act - добавляем новую версию
    v3_dir = api_dir / "v3"
    v3_dir.mkdir(parents=True, exist_ok=True)
    (v3_dir / "api_config.yaml").write_text("openapi: '3.1.0'\ninfo:\n  title: Test API v3\n  version: '1.0.0'\npaths: {}")
    
    html_generator.update_index("v3")
    
    # Assert
    updated_content = index_file.read_text(encoding='utf-8')
    assert "api/v1/index.html" in updated_content
    assert "api/v2/index.html" in updated_content  
    assert "api/v3/index.html" in updated_content
    
    # Проверяем, что создался index.html для новой версии
    v3_index = v3_dir / "index.html"
    assert v3_index.exists()
    v3_content = v3_index.read_text(encoding='utf-8')
    assert "API v3" in v3_content


def test_html_generator_version_sorting(temp_dir: Path):
    """Тест проверяет правильную сортировку версий в индексной странице."""
    # Arrange
    docs_dir = temp_dir / "docs"
    api_dir = docs_dir / "api"
    
    # Создаем версии в произвольном порядке
    versions = ["v10", "v2", "v1", "v3"]
    for version in versions:
        version_dir = api_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        (version_dir / "api_config.yaml").write_text("openapi: '3.1.0'\ninfo:\n  title: Test\npaths: {}")
    
    # Act
    html_generator = HTMLGenerator(api_dir)
    html_generator.update_index()
    
    # Assert
    index_file = docs_dir / "index.html"
    content = index_file.read_text(encoding='utf-8')
    
    # Проверяем, что версии отсортированы правильно (v1, v2, v3, v10)
    v1_pos = content.find("api/v1/index.html")
    v2_pos = content.find("api/v2/index.html") 
    v3_pos = content.find("api/v3/index.html")
    v10_pos = content.find("api/v10/index.html")
    
    assert v1_pos < v2_pos < v3_pos < v10_pos


def test_html_generator_empty_directory(temp_dir: Path):
    """Тест проверяет поведение HTMLGenerator с пустой директорией."""
    # Arrange
    docs_dir = temp_dir / "docs"
    api_dir = docs_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    
    # Act
    html_generator = HTMLGenerator(api_dir)
    html_generator.update_index()
    
    # Assert
    index_file = docs_dir / "index.html"
    assert index_file.exists()
    
    content = index_file.read_text(encoding='utf-8')
    assert "API versions list" in content
    assert "<table>" in content
    # Не должно быть ссылок на версии
    assert "api/v" not in content
    
    # Assets должны быть скопированы даже для пустой директории
    assets_dir = docs_dir / "assets"
    assert assets_dir.exists()


def test_html_generator_unicode_support(temp_dir: Path):
    """Тест проверяет поддержку Unicode в генерируемых HTML страницах."""
    # Arrange
    docs_dir = temp_dir / "docs"
    api_dir = docs_dir / "api"
    v1_dir = api_dir / "v1"
    v1_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаем спецификацию с русскими символами
    spec_content = {
        "openapi": "3.1.0",
        "info": {
            "title": "Тестовое API",
            "description": "API для тестирования русских символов",
            "version": "1.0.0"
        },
        "paths": {
            "/пользователи": {
                "get": {
                    "summary": "Получить пользователей"
                }
            }
        }
    }
    
    spec_file = v1_dir / "api_config.yaml"
    with spec_file.open('w', encoding='utf-8') as f:
        yaml.dump(spec_content, f, allow_unicode=True)
    
    # Act
    html_generator = HTMLGenerator(api_dir)
    html_generator.update_index("v1")
    
    # Assert
    v1_index = v1_dir / "index.html"
    assert v1_index.exists()
    
    content = v1_index.read_text(encoding='utf-8')
    assert "API v1" in content
    assert 'charset="UTF-8"' in content
    assert "swagger-ui" in content


def test_html_generator_assets_copy(temp_dir: Path):
    """Тест проверяет корректное копирование Swagger UI ресурсов."""
    # Arrange
    docs_dir = temp_dir / "docs"
    api_dir = docs_dir / "api"
    v1_dir = api_dir / "v1"
    v1_dir.mkdir(parents=True, exist_ok=True)
    
    (v1_dir / "api_config.yaml").write_text("openapi: '3.1.0'\ninfo:\n  title: Test\npaths: {}")
    
    # Act
    html_generator = HTMLGenerator(api_dir)
    html_generator.ensure_assets()
    
    # Assert
    assets_dir = docs_dir / "assets"
    assert assets_dir.exists()
    assert assets_dir.is_dir()
    
    # Проверяем основные файлы Swagger UI
    required_files = [
        "swagger-ui.css",
        "swagger-ui-bundle.js", 
        "swagger-ui-standalone-preset.js",
        "favicon-16x16.png",
        "favicon-32x32.png"
    ]
    
    for file_name in required_files:
        file_path = assets_dir / file_name
        assert file_path.exists(), f"Missing asset file: {file_name}"


def test_html_generator_version_page_content(temp_dir: Path):
    """Тест проверяет содержимое генерируемой страницы версии API."""
    # Arrange
    docs_dir = temp_dir / "docs"
    api_dir = docs_dir / "api"
    v1_dir = api_dir / "v1"
    v1_dir.mkdir(parents=True, exist_ok=True)
    
    spec_content = {
        "openapi": "3.1.0",
        "info": {
            "title": "Advanced Test API",
            "version": "2.0.0"
        },
        "paths": {
            "/users": {"get": {"summary": "Get users"}},
            "/items": {"post": {"summary": "Create item"}}
        }
    }
    
    spec_file = v1_dir / "api_config.yaml"
    with spec_file.open('w', encoding='utf-8') as f:
        yaml.dump(spec_content, f, allow_unicode=True)
    
    # Act
    html_generator = HTMLGenerator(api_dir)
    html_generator.generate_version_page(v1_dir)
    
    # Assert
    version_page = v1_dir / "index.html"
    assert version_page.exists()
    
    content = version_page.read_text(encoding='utf-8')
    
    # Проверяем структуру HTML
    assert "<!DOCTYPE html>" in content
    assert 'lang="en"' in content
    assert 'charset="UTF-8"' in content
    assert "API v1" in content
    
    # Проверяем подключение Swagger UI ресурсов
    assert 'href="../../assets/swagger-ui.css"' in content
    assert 'src="../../assets/swagger-ui-bundle.js"' in content
    assert 'src="../../assets/swagger-ui-standalone-preset.js"' in content
    
    # Проверяем конфигурацию Swagger UI
    assert 'url: "api_config.yaml"' in content
    assert "dom_id: '#swagger-ui'" in content
    assert "SwaggerUIBundle" in content
    assert "deepLinking: true" in content
