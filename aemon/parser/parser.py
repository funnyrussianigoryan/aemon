import argparse
from typing import Union, Dict, Callable

from aemon.parser.dto import GenerateCommandArgs, RenderHtmlCommandArgs


class AemonCLIParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="aemon",
            description="Aemon — CLI-tool for OpenAPI spec generation",
        )
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        
        # DTO dispatch mapping
        self._dto_dispatch: Dict[str, Callable] = {
            "generate": self._create_generate_dto,
            "render-html": self._create_render_html_dto,
        }

        self._register_generate_command()
        self._register_other_commands()

    def parse(self) -> Union[GenerateCommandArgs, RenderHtmlCommandArgs]:
        args = self.parser.parse_args()
        
        if args.command not in self._dto_dispatch:
            raise ValueError(f"Unknown command: {args.command}")
        
        return self._dto_dispatch[args.command](args)
    
    def _create_generate_dto(self, args) -> GenerateCommandArgs:
        """Create GenerateCommandArgs DTO from parsed arguments."""
        return GenerateCommandArgs(
            command="generate",
            module=args.module,
            app=args.app
        )
    
    def _create_render_html_dto(self, args) -> RenderHtmlCommandArgs:
        """Create RenderHtmlCommandArgs DTO from parsed arguments."""
        return RenderHtmlCommandArgs(
            command="render-html",
            output_dir=args.output_dir
        )

    def _register_generate_command(self):
        generate = self.subparsers.add_parser("generate", help="Generate OpenAPI spec")
        generate.add_argument(
            "--module",
            "-m",
            required=True,
            help="FastAPI-app module path (for example, main.py)",
        )
        generate.add_argument(
            "--app",
            "-a",
            default="app",
            help="FastAPI variable name (default 'app')",
        )

    def _register_other_commands(self):
        render = self.subparsers.add_parser("render-html", help="Regenerate index.html without new API")
        render.add_argument("--output-dir", default="docs/api", help="Path of directory with OpenAPI specs")

