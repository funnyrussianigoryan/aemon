import argparse
from typing import Union

from aemon.parser.dto import GenerateCommandArgs, RenderHtmlCommandArgs


class AemonCLIParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="aemon",
            description="Aemon — CLI-tool for OpenAPI spec generation",
        )
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)

        self._register_generate_command()

    def parse(self) -> Union[GenerateCommandArgs, RenderHtmlCommandArgs]:
            args = self.parser.parse_args()

            dispatch = {
                "generate": lambda a: GenerateCommandArgs(
                    command="generate",
                    module=a.module,
                    app=a.app
                ),
                "render-html": lambda a: RenderHtmlCommandArgs(
                    command="render-html",
                    output_dir=a.output_dir
                ),
            }

            return dispatch[args.command](args)  # type: ignore[return-value]

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
        render.add_argument("--output-dir", efault="docs/api", help="Path of directory with OpenAPI specs")

