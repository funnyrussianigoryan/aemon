from abc import ABC, abstractmethod
from argparse import Namespace
from typing import Union

from aemon.parser.dto import GenerateCommandArgs, RenderHtmlCommandArgs


class CommandHandler(ABC):
    """Абстрактный базовый класс для обработчиков команд."""
    
    @abstractmethod
    def handle(self, args: Namespace) -> Union[GenerateCommandArgs, RenderHtmlCommandArgs]:
        """Обрабатывает аргументы команды и возвращает соответствующий DTO."""
        pass


class GenerateCommandHandler(CommandHandler):
    """Обработчик команды generate."""
    
    def handle(self, args: Namespace) -> GenerateCommandArgs:
        return GenerateCommandArgs(
            command="generate",
            module=args.module,
            app=args.app
        )


class RenderHtmlCommandHandler(CommandHandler):
    """Обработчик команды render-html."""
    
    def handle(self, args: Namespace) -> RenderHtmlCommandArgs:
        return RenderHtmlCommandArgs(
            command="render-html",
            output_dir=args.output_dir
        )


class CommandDispatcher:
    """Диспетчер команд для CLI."""
    
    def __init__(self):
        self._handlers = {
            "generate": GenerateCommandHandler(),
            "render-html": RenderHtmlCommandHandler(),
        }
    
    def dispatch(self, args: Namespace) -> Union[GenerateCommandArgs, RenderHtmlCommandArgs]:
        """
        Диспетчеризация команды на соответствующий обработчик.
        
        Args:
            args: Аргументы командной строки, полученные от argparse
            
        Returns:
            Объект DTO соответствующей команды
            
        Raises:
            KeyError: Если команда не зарегистрирована
        """
        if args.command not in self._handlers:
            raise KeyError(f"Unknown command: {args.command}")
        
        handler = self._handlers[args.command]
        return handler.handle(args)
    
    def register_handler(self, command: str, handler: CommandHandler) -> None:
        """
        Регистрирует новый обработчик команды.
        
        Args:
            command: Название команды
            handler: Обработчик команды
        """
        self._handlers[command] = handler
    
    def get_registered_commands(self) -> list[str]:
        """Возвращает список зарегистрированных команд."""
        return list(self._handlers.keys())
