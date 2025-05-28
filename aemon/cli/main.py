import logging

from aemon.config.loader import ConfigLoader
from aemon.core.generator import OpenAPIGenerator
from aemon.output.html_generator import HTMLGenerator
from aemon.parser.dto import GenerateCommandArgs, RenderHtmlCommandArgs
from aemon.parser.parser import AemonCLIParser


def main():
    logging.basicConfig(level=logging.INFO)

    args = AemonCLIParser().parse()

    if isinstance(args, GenerateCommandArgs):
        config = ConfigLoader()

        generator = OpenAPIGenerator(
            module_path=args.module,
            app_name=args.app,
            config=config,
        )
        version = generator.generate()

        HTMLGenerator(config.get_output_dir()).update_index(version)

    elif isinstance(args, RenderHtmlCommandArgs):
        HTMLGenerator(args.output_dir).update_index()
