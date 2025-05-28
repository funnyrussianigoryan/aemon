from dataclasses import dataclass
from typing import Literal


@dataclass
class GenerateCommandArgs:
    command: Literal["generate"]
    module: str
    app: str = "app"


@dataclass
class RenderHtmlCommandArgs:
    command: Literal["render-html"]
    output_dir: str = "docs/api"
