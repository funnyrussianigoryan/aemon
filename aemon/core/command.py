from abc import ABC, abstractmethod
from typing import Any

from aemon.parser.dto import GenerateCommandArgs, RenderHtmlCommandArgs


class BaseCommand(ABC):
    """Base abstract class for all commands."""
    
    @abstractmethod
    def execute(self) -> Any:
        """Execute the command and return result."""
        pass


class GenerateCommand(BaseCommand):
    """Command for generating OpenAPI specs."""
    
    def __init__(self, args: GenerateCommandArgs):
        self.args = args
    
    def execute(self) -> Any:
        from aemon.config.loader import ConfigLoader
        from aemon.core.generator import OpenAPIGenerator
        from aemon.output.html_generator import HTMLGenerator
        
        config = ConfigLoader()
        
        generator = OpenAPIGenerator(
            module_path=self.args.module,
            app_name=self.args.app,
            config=config,
        )
        version = generator.generate()
        
        HTMLGenerator(config.get_output_dir()).update_index(version)
        return version


class RenderHtmlCommand(BaseCommand):
    """Command for rendering HTML without generating new API specs."""
    
    def __init__(self, args: RenderHtmlCommandArgs):
        self.args = args
    
    def execute(self) -> Any:
        from aemon.output.html_generator import HTMLGenerator
        
        # Implementation for render-html command
        generator = HTMLGenerator(self.args.output_dir)
        # Add logic to regenerate index.html
        return None