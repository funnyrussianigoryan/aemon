from typing import Dict, Type, Union

from aemon.core.command import BaseCommand, GenerateCommand, RenderHtmlCommand
from aemon.parser.dto import GenerateCommandArgs, RenderHtmlCommandArgs


class CommandDispatcher:
    """Dispatcher class for routing and executing commands."""
    
    def __init__(self):
        self._command_registry: Dict[str, Type[BaseCommand]] = {
            "generate": GenerateCommand,
            "render-html": RenderHtmlCommand,
        }
    
    def dispatch(self, args: Union[GenerateCommandArgs, RenderHtmlCommandArgs]) -> any:
        """
        Dispatch and execute a command based on the arguments.
        
        Args:
            args: Command arguments object
            
        Returns:
            Result of command execution
            
        Raises:
            ValueError: If command is not registered
        """
        command_name = args.command
        
        if command_name not in self._command_registry:
            raise ValueError(f"Unknown command: {command_name}")
        
        command_class = self._command_registry[command_name]
        command_instance = command_class(args)
        
        return command_instance.execute()
    
    def register_command(self, command_name: str, command_class: Type[BaseCommand]) -> None:
        """
        Register a new command in the dispatcher.
        
        Args:
            command_name: Name of the command
            command_class: Command class that implements BaseCommand
        """
        self._command_registry[command_name] = command_class
    
    def get_available_commands(self) -> list[str]:
        """Get list of available command names."""
        return list(self._command_registry.keys())