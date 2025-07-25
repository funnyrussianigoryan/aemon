"""Enhanced main CLI module with comprehensive command support."""
import json
import logging
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Any, Dict

import yaml

from aemon.config.loader import ConfigLoader
from aemon.core.exceptions import AemonError
from aemon.core.generator import OpenAPIGenerator
from aemon.output.html_generator import HTMLGenerator
from aemon.parser.dto import (
    GenerateCommandArgs,
    InitCommandArgs,
    ListCommandArgs,
    RenderHtmlCommandArgs,
    ServeCommandArgs,
    ValidateCommandArgs,
)
from aemon.parser.parser import AemonCLIParser


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" if verbose else "%(message)s"
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def handle_generate_command(args: GenerateCommandArgs) -> int:
    """Handle generate command."""
    try:
        config = ConfigLoader(args.config)
        
        generator = OpenAPIGenerator(
            module_path=args.module,
            app_name=args.app,
            config=config,
        )
        
        version = generator.generate(force_regenerate=args.force)
        
        if args.validate:
            validation_result = generator.validate_spec(version)
            if not validation_result["valid"]:
                logging.error(f"Generated spec validation failed: {validation_result['errors']}")
                return 1
            elif validation_result["warnings"]:
                logging.warning(f"Generated spec has warnings: {validation_result['warnings']}")
        
        # Generate HTML
        html_generator = HTMLGenerator(
            config.get_output_dir(), 
            config._config
        )
        html_generator.update_index(version)
        
        logging.info(f"✅ Successfully generated API documentation version {version}")
        logging.info(f"📁 Output directory: {config.get_output_dir().absolute()}")
        logging.info(f"🌐 Open in browser: file://{config.get_output_dir().parent.absolute()}/index.html")
        
        return 0
        
    except AemonError as e:
        logging.error(f"❌ Generation failed: {e}")
        return 1
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def handle_render_html_command(args: RenderHtmlCommandArgs) -> int:
    """Handle render-html command."""
    try:
        config = ConfigLoader(args.config)
        
        html_generator = HTMLGenerator(
            Path(args.output_dir),
            config._config
        )
        html_generator.update_index()
        
        logging.info("✅ Successfully regenerated HTML index")
        return 0
        
    except Exception as e:
        logging.error(f"❌ HTML generation failed: {e}")
        return 1


def handle_validate_command(args: ValidateCommandArgs) -> int:
    """Handle validate command."""
    try:
        config = ConfigLoader(args.config)
        generator = OpenAPIGenerator("", "", config)  # Dummy generator for validation
        
        if args.version:
            versions = [args.version]
        else:
            versions = generator.get_existing_versions()
            
        if not versions:
            logging.warning("No versions found to validate")
            return 0
        
        all_valid = True
        
        for version in versions:
            validation_result = generator.validate_spec(version)
            
            if validation_result["valid"]:
                logging.info(f"✅ {version}: Valid")
                if validation_result["warnings"]:
                    for warning in validation_result["warnings"]:
                        logging.warning(f"⚠️  {version}: {warning}")
                        if args.strict:
                            all_valid = False
            else:
                logging.error(f"❌ {version}: Invalid")
                for error in validation_result["errors"]:
                    logging.error(f"   • {error}")
                all_valid = False
        
        return 0 if all_valid else 1
        
    except Exception as e:
        logging.error(f"❌ Validation failed: {e}")
        return 1


def handle_list_command(args: ListCommandArgs) -> int:
    """Handle list command."""
    try:
        config = ConfigLoader(args.config)
        generator = OpenAPIGenerator("", "", config)  # Dummy generator
        
        versions = generator.get_existing_versions()
        
        if not versions:
            logging.info("No API versions found")
            return 0
        
        if args.format == "table":
            print_table_format(generator, versions, args.detailed)
        elif args.format == "json":
            print_json_format(generator, versions, args.detailed)
        elif args.format == "yaml":
            print_yaml_format(generator, versions, args.detailed)
            
        return 0
        
    except Exception as e:
        logging.error(f"❌ Failed to list versions: {e}")
        return 1


def print_table_format(generator: OpenAPIGenerator, versions: list, detailed: bool) -> None:
    """Print versions in table format."""
    if detailed:
        print(f"{'Version':<10} {'Generated':<20} {'Routes':<8} {'Module':<30}")
        print("-" * 70)
        
        for version in versions:
            info = generator.get_spec_info(version)
            if info:
                generated = info.get("generated_at", "Unknown")[:19]
                routes = info.get("routes_count", "Unknown")
                module = info.get("module_path", "Unknown")
                print(f"{version:<10} {generated:<20} {routes:<8} {module:<30}")
            else:
                print(f"{version:<10} {'Unknown':<20} {'Unknown':<8} {'Unknown':<30}")
    else:
        print("Available API versions:")
        for version in versions:
            print(f"  • {version}")


def print_json_format(generator: OpenAPIGenerator, versions: list, detailed: bool) -> None:
    """Print versions in JSON format."""
    if detailed:
        data = []
        for version in versions:
            info = generator.get_spec_info(version) or {}
            data.append({"version": version, **info})
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"versions": versions}, indent=2))


def print_yaml_format(generator: OpenAPIGenerator, versions: list, detailed: bool) -> None:
    """Print versions in YAML format."""
    if detailed:
        data = []
        for version in versions:
            info = generator.get_spec_info(version) or {}
            data.append({"version": version, **info})
        print(yaml.dump(data, default_flow_style=False, allow_unicode=True))
    else:
        print(yaml.dump({"versions": versions}, default_flow_style=False))


def handle_serve_command(args: ServeCommandArgs) -> int:
    """Handle serve command."""
    try:
        config = ConfigLoader(args.config)
        docs_dir = config.get_output_dir().parent
        
        if not docs_dir.exists() or not (docs_dir / "index.html").exists():
            logging.error("❌ No documentation found. Run 'aemon generate' first.")
            return 1
        
        class DocumentationHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(docs_dir), **kwargs)
                
            def log_message(self, format, *args):
                # Suppress default server logs unless verbose
                if args[1] == '200':  # Only log successful requests in verbose mode
                    pass
        
        server = HTTPServer((args.host, args.port), DocumentationHandler)
        
        url = f"http://{args.host}:{args.port}"
        logging.info(f"🚀 Serving documentation at {url}")
        logging.info("Press Ctrl+C to stop the server")
        
        if args.open_browser:
            Thread(target=lambda: webbrowser.open(url), daemon=True).start()
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logging.info("\n👋 Server stopped")
            return 0
            
    except Exception as e:
        logging.error(f"❌ Failed to start server: {e}")
        return 1


def handle_init_command(args: InitCommandArgs) -> int:
    """Handle init command."""
    try:
        config_filename = f"aemon.{args.format}"
        config_path = Path(config_filename)
        
        if config_path.exists() and not args.force:
            logging.error(f"❌ Configuration file {config_filename} already exists. Use --force to overwrite.")
            return 1
        
        # Create default configuration
        config = ConfigLoader()
        config.save_config(config_path)
        
        logging.info(f"✅ Created configuration file: {config_filename}")
        logging.info("You can now customize the configuration and run 'aemon generate'")
        
        return 0
        
    except Exception as e:
        logging.error(f"❌ Failed to initialize configuration: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    try:
        parser = AemonCLIParser()
        args = parser.parse()
        
        # Setup logging based on verbosity
        setup_logging(getattr(args, 'verbose', False))
        
        # Route to appropriate handler
        if isinstance(args, GenerateCommandArgs):
            return handle_generate_command(args)
        elif isinstance(args, RenderHtmlCommandArgs):
            return handle_render_html_command(args)
        elif isinstance(args, ValidateCommandArgs):
            return handle_validate_command(args)
        elif isinstance(args, ListCommandArgs):
            return handle_list_command(args)
        elif isinstance(args, ServeCommandArgs):
            return handle_serve_command(args)
        elif isinstance(args, InitCommandArgs):
            return handle_init_command(args)
        else:
            logging.error(f"❌ Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        logging.info("\n👋 Operation cancelled by user")
        return 130
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

