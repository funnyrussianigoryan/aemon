"""Data transfer objects for CLI commands."""
from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class GenerateCommandArgs:
    """Arguments for generate command."""
    command: Literal["generate"]
    module: str
    app: str = "app"
    force: bool = False
    validate: bool = True
    config: Optional[str] = None
    verbose: bool = False


@dataclass
class RenderHtmlCommandArgs:
    """Arguments for render-html command."""
    command: Literal["render-html"]
    output_dir: str = "docs/api"
    config: Optional[str] = None
    verbose: bool = False


@dataclass
class ValidateCommandArgs:
    """Arguments for validate command."""
    command: Literal["validate"]
    version: Optional[str] = None
    strict: bool = False
    config: Optional[str] = None
    verbose: bool = False


@dataclass
class ListCommandArgs:
    """Arguments for list command."""
    command: Literal["list"]
    format: Literal["table", "json", "yaml"] = "table"
    detailed: bool = False
    config: Optional[str] = None
    verbose: bool = False


@dataclass
class ServeCommandArgs:
    """Arguments for serve command."""
    command: Literal["serve"]
    port: int = 8080
    host: str = "localhost"
    open_browser: bool = False
    config: Optional[str] = None
    verbose: bool = False


@dataclass
class InitCommandArgs:
    """Arguments for init command."""
    command: Literal["init"]
    format: Literal["yaml", "json"] = "yaml"
    force: bool = False
    config: Optional[str] = None
    verbose: bool = False
