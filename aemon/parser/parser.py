"""Enhanced CLI parser with comprehensive commands and validation."""
import argparse
import sys
from typing import Union

from aemon.parser.dto import (
    GenerateCommandArgs, 
    RenderHtmlCommandArgs,
    ValidateCommandArgs,
    ListCommandArgs,
    ServeCommandArgs,
    InitCommandArgs
)


class AemonCLIParser:
    """Enhanced CLI parser with comprehensive command support."""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="aemon",
            description="Aemon — Enhanced CLI tool for OpenAPI spec generation and documentation",
            epilog="""
Examples:
  aemon generate -m main.py                    # Generate API docs from main.py
  aemon generate -m myapp/main.py -a api       # Use 'api' variable instead of 'app'
  aemon generate -m myapp.main --force         # Force regeneration
  aemon render-html                            # Regenerate HTML without new API
  aemon validate v1                            # Validate specific version
  aemon list                                   # List all versions
  aemon serve                                  # Start development server
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Global options
        self.parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        
        self.parser.add_argument(
            "--config", "-c",
            help="Path to configuration file"
        )
        
        self.subparsers = self.parser.add_subparsers(
            dest="command", 
            required=True,
            help="Available commands"
        )

        self._register_generate_command()
        self._register_render_command()
        self._register_validate_command()
        self._register_list_command()
        self._register_serve_command()
        self._register_init_command()

    def parse(self) -> Union[GenerateCommandArgs, RenderHtmlCommandArgs, ValidateCommandArgs, ListCommandArgs, ServeCommandArgs, InitCommandArgs]:
        """Parse command line arguments."""
        if len(sys.argv) == 1:
            self.parser.print_help()
            sys.exit(1)
            
        args = self.parser.parse_args()

        dispatch = {
            "generate": lambda a: GenerateCommandArgs(
                command="generate",
                module=a.module,
                app=getattr(a, 'app', 'app'),
                force=getattr(a, 'force', False),
                validate=getattr(a, 'validate', True),
                config=getattr(a, 'config', None),
                verbose=getattr(a, 'verbose', False)
            ),
            "render-html": lambda a: RenderHtmlCommandArgs(
                command="render-html",
                output_dir=getattr(a, 'output_dir', 'docs/api'),
                config=getattr(a, 'config', None),
                verbose=getattr(a, 'verbose', False)
            ),
            "validate": lambda a: ValidateCommandArgs(
                command="validate",
                version=getattr(a, 'version', None),
                strict=getattr(a, 'strict', False),
                config=getattr(a, 'config', None),
                verbose=getattr(a, 'verbose', False)
            ),
            "list": lambda a: ListCommandArgs(
                command="list",
                format=getattr(a, 'format', 'table'),
                detailed=getattr(a, 'detailed', False),
                config=getattr(a, 'config', None),
                verbose=getattr(a, 'verbose', False)
            ),
            "serve": lambda a: ServeCommandArgs(
                command="serve",
                port=getattr(a, 'port', 8080),
                host=getattr(a, 'host', 'localhost'),
                open_browser=getattr(a, 'open', False),
                config=getattr(a, 'config', None),
                verbose=getattr(a, 'verbose', False)
            ),
            "init": lambda a: InitCommandArgs(
                command="init",
                format=getattr(a, 'format', 'yaml'),
                force=getattr(a, 'force', False),
                config=getattr(a, 'config', None),
                verbose=getattr(a, 'verbose', False)
            ),
        }

        return dispatch[args.command](args)  # type: ignore[return-value]

    def _register_generate_command(self):
        """Register generate command."""
        generate = self.subparsers.add_parser(
            "generate", 
            help="Generate OpenAPI specification and documentation",
            description="Generate OpenAPI spec from FastAPI application"
        )
        
        generate.add_argument(
            "--module", "-m",
            required=True,
            help="FastAPI app module path (e.g., main.py or myapp.main)"
        )
        
        generate.add_argument(
            "--app", "-a",
            default="app",
            help="FastAPI variable name (default: 'app')"
        )
        
        generate.add_argument(
            "--force", "-f",
            action="store_true",
            help="Force regeneration even if version already exists"
        )
        
        generate.add_argument(
            "--no-validate",
            action="store_false",
            dest="validate",
            help="Skip validation of generated spec"
        )

    def _register_render_command(self):
        """Register render-html command."""
        render = self.subparsers.add_parser(
            "render-html", 
            help="Regenerate HTML index without creating new API version",
            description="Update the HTML index page with existing API versions"
        )
        
        render.add_argument(
            "--output-dir", 
            default="docs/api", 
            help="Path to directory with OpenAPI specs (default: docs/api)"
        )

    def _register_validate_command(self):
        """Register validate command."""
        validate = self.subparsers.add_parser(
            "validate",
            help="Validate OpenAPI specification",
            description="Validate OpenAPI spec for specific version or all versions"
        )
        
        validate.add_argument(
            "version",
            nargs="?",
            help="Version to validate (e.g., v1). If not specified, validates all versions"
        )
        
        validate.add_argument(
            "--strict",
            action="store_true",
            help="Enable strict validation with warnings as errors"
        )

    def _register_list_command(self):
        """Register list command."""
        list_cmd = self.subparsers.add_parser(
            "list",
            help="List all available API versions",
            description="Display all generated API versions with metadata"
        )
        
        list_cmd.add_argument(
            "--format",
            choices=["table", "json", "yaml"],
            default="table",
            help="Output format (default: table)"
        )
        
        list_cmd.add_argument(
            "--detailed",
            action="store_true",
            help="Show detailed information for each version"
        )

    def _register_serve_command(self):
        """Register serve command."""
        serve = self.subparsers.add_parser(
            "serve",
            help="Start development server for documentation",
            description="Start a local HTTP server to serve the generated documentation"
        )
        
        serve.add_argument(
            "--port", "-p",
            type=int,
            default=8080,
            help="Port to serve on (default: 8080)"
        )
        
        serve.add_argument(
            "--host",
            default="localhost",
            help="Host to bind to (default: localhost)"
        )
        
        serve.add_argument(
            "--open", "-o",
            action="store_true",
            help="Open browser automatically"
        )

    def _register_init_command(self):
        """Register init command."""
        init = self.subparsers.add_parser(
            "init",
            help="Initialize aemon configuration",
            description="Create initial configuration file with default settings"
        )
        
        init.add_argument(
            "--format",
            choices=["yaml", "json"],
            default="yaml",
            help="Configuration file format (default: yaml)"
        )
        
        init.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing configuration file"
        )

