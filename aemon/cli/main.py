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
        from pathlib import Path
        output_path = Path(args.output_dir)
        html_generator = HTMLGenerator(output_path)
        # Получаем все доступные версии API и обновляем индекс
        # В данном случае передаем None, так как мы только регенерируем HTML
        html_generator.update_index(None)
        logging.info(f"HTML regenerated in {args.output_dir}")

