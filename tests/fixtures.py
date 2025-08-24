import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock

import pytest

from aemon.config.loader import ConfigLoader


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Создает временную директорию для тестов."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def test_fastapi_app_file(temp_dir: Path) -> Path:
    """Создает тестовое FastAPI приложение с двумя эндпоинтами."""
    app_content = '''
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Test API", description="API for testing aemon", version="1.0.0")

class UserCreate(BaseModel):
    name: str
    email: str

class User(BaseModel):
    id: int
    name: str
    email: str

class ItemCreate(BaseModel):
    title: str
    description: str

class Item(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int

@app.get("/users/{user_id}", response_model=User, tags=["users"])
async def get_user(user_id: int):
    """Get user by ID."""
    return User(id=user_id, name="John Doe", email="john@example.com")

@app.post("/users", response_model=User, tags=["users"])
async def create_user(user: UserCreate):
    """Create new user."""
    return User(id=1, name=user.name, email=user.email)

@app.get("/items/{item_id}", response_model=Item, tags=["items"])
async def get_item(item_id: int):
    """Get item by ID."""
    return Item(id=item_id, title="Test Item", description="Test Description", owner_id=1)

@app.post("/items", response_model=Item, tags=["items"])
async def create_item(item: ItemCreate):
    """Create new item."""
    return Item(id=1, title=item.title, description=item.description, owner_id=1)
'''
    
    app_file = temp_dir / "test_app.py"
    app_file.write_text(app_content.strip(), encoding='utf-8')
    return app_file


@pytest.fixture
def test_config_file(temp_dir: Path) -> Path:
    """Создает тестовый файл конфигурации setup.cfg."""
    config_content = f'''
[aemon]
output_dir = {temp_dir / "docs" / "api"}
'''
    
    config_file = temp_dir / "setup.cfg"
    config_file.write_text(config_content.strip())
    return config_file


@pytest.fixture
def mock_config_loader(test_config_file: Path):
    """Мокает ConfigLoader для использования тестовой конфигурации."""
    mocked_config_loader = Mock(spec=ConfigLoader)
    mocked_config_loader.get_output_dir.return_value = test_config_file.parent / "docs" / "api"
    mocked_config_loader.get_version.return_value = "v1"
    return mocked_config_loader
