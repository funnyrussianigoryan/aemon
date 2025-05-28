import argparse
from typing import Union

from aemon.parser.dto import GenerateCommandArgs, RenderHtmlCommandArgs


class AemonCLIParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="aemon",
            description="Aemon — CLI-инструмент для генерации OpenAPI и документации",
        )
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)

        self._register_generate_command()

    def _register_generate_command(self):
        generate = self.subparsers.add_parser("generate", help="Сгенерировать OpenAPI спецификацию")
        generate.add_argument(
            "--module",
            "-m",
            required=True,
            help="Путь к модулю FastAPI-приложения (например, main.py)",
        )
        generate.add_argument(
            "--app",
            "-a",
            default="app",
            help="Имя переменной FastAPI-приложения (по умолчанию 'app')",
        )

    def _register_other_commands(self):
        render = self.subparsers.add_parser("render-html", help="Перегенерировать index.html без нового API")
        render.add_argument("--output-dir", efault="docs/api", help="Путь к директории с версиями OpenAPI")

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

            return dispatch[args.command](args)
