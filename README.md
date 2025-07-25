# Aemon - Enhanced FastAPI Documentation Generator

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-red.svg)

Aemon is a powerful CLI tool for generating beautiful, versioned OpenAPI documentation from FastAPI applications. It creates interactive Swagger UI documentation with modern design, dark theme support, and comprehensive version management.

## ✨ Features

- 🚀 **One-command generation** - Generate complete documentation from FastAPI apps
- 📚 **Version management** - Automatic versioning with clean organization
- 🎨 **Modern UI** - Beautiful, responsive interface with dark/light theme
- 🔍 **Search & filtering** - Find API versions quickly
- ⚡ **Development server** - Built-in server for local testing
- 🛠️ **Flexible configuration** - YAML, JSON, or INI configuration files
- ✅ **Validation** - Built-in OpenAPI spec validation
- 📱 **Responsive design** - Works perfectly on mobile devices
- 🌙 **Dark theme** - Automatic theme switching with persistence
- 📖 **Multiple formats** - Export in YAML and JSON formats

## 🚀 Quick Start

### Installation

```bash
pip install aemon
```

### Basic Usage

1. **Initialize configuration** (optional):
```bash
aemon init
```

2. **Generate documentation**:
```bash
aemon generate -m main.py
```

3. **Start development server**:
```bash
aemon serve --open
```

## 📖 Commands

### `generate` - Generate API Documentation

Generate OpenAPI specification and HTML documentation from your FastAPI app.

```bash
aemon generate -m main.py                    # Basic generation
aemon generate -m myapp/main.py -a api       # Custom app variable
aemon generate -m myapp.main --force         # Force regeneration
aemon generate -m main.py --no-validate      # Skip validation
```

**Options:**
- `-m, --module` - Path to FastAPI module (required)
- `-a, --app` - FastAPI app variable name (default: "app")
- `-f, --force` - Force regeneration even if version exists
- `--no-validate` - Skip OpenAPI spec validation

### `render-html` - Regenerate HTML

Update the HTML index page without generating new API version.

```bash
aemon render-html                           # Use default output dir
aemon render-html --output-dir custom/path  # Custom output directory
```

### `validate` - Validate Specifications

Validate OpenAPI specifications for quality and correctness.

```bash
aemon validate              # Validate all versions
aemon validate v1           # Validate specific version
aemon validate --strict     # Treat warnings as errors
```

### `list` - List API Versions

Display all generated API versions with metadata.

```bash
aemon list                  # Simple table format
aemon list --detailed       # Detailed information
aemon list --format json    # JSON output
aemon list --format yaml    # YAML output
```

### `serve` - Development Server

Start a local HTTP server to serve the documentation.

```bash
aemon serve                 # Start on localhost:8080
aemon serve -p 3000         # Custom port
aemon serve --open          # Open browser automatically
aemon serve --host 0.0.0.0  # Bind to all interfaces
```

### `init` - Initialize Configuration

Create a configuration file with default settings.

```bash
aemon init                  # Create aemon.yaml
aemon init --format json    # Create aemon.json
aemon init --force          # Overwrite existing config
```

## ⚙️ Configuration

Aemon supports multiple configuration formats. Create a configuration file to customize behavior:

### YAML Configuration (`aemon.yaml`)

```yaml
aemon:
  # Output directory for generated documentation
  output_dir: "docs/api"
  
  # Documentation metadata
  title: "My API Documentation"
  description: "Comprehensive API documentation"
  
  # Version configuration
  version_prefix: "v"
  auto_increment: true
  
  # Swagger UI customization
  swagger_ui_config:
    deepLinking: true
    docExpansion: "none"
    filter: true
    tryItOutEnabled: true
  
  # Optional: Contact and license info
  contact:
    name: "API Support"
    email: "support@example.com"
  
  license:
    name: "MIT"
    url: "https://opensource.org/licenses/MIT"
```

### JSON Configuration (`aemon.json`)

```json
{
  "aemon": {
    "output_dir": "docs/api",
    "title": "My API Documentation",
    "swagger_ui_config": {
      "deepLinking": true,
      "docExpansion": "none"
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_dir` | string | `"docs/api"` | Output directory for documentation |
| `title` | string | `"API Documentation"` | Documentation title |
| `description` | string | `"Generated API documentation"` | Documentation description |
| `version_prefix` | string | `"v"` | Version prefix (e.g., "v1", "v2") |
| `auto_increment` | boolean | `true` | Automatically increment version numbers |
| `include_schemas` | boolean | `true` | Include schema definitions |
| `swagger_ui_config` | object | `{}` | Swagger UI configuration options |

## 🎨 UI Features

### Modern Interface
- Clean, professional design
- Responsive layout for all devices
- Intuitive navigation between versions

### Dark Theme Support
- Automatic theme detection
- Manual theme toggle
- Persistent theme preferences
- Keyboard shortcut: `Ctrl/Cmd + D`

### Search & Navigation
- Real-time version search
- Keyboard shortcut: `Ctrl/Cmd + K`
- Quick access to YAML/JSON downloads
- Back navigation in Swagger UI

## 📁 Output Structure

```
docs/
├── index.html              # Main index page
├── assets/                 # Swagger UI assets
│   ├── swagger-ui.css
│   ├── swagger-ui-bundle.js
│   └── ...
└── api/
    ├── v1/
    │   ├── index.html       # Swagger UI page
    │   ├── api_config.yaml  # OpenAPI spec (YAML)
    │   ├── api_config.json  # OpenAPI spec (JSON)
    │   └── metadata.json    # Generation metadata
    ├── v2/
    │   └── ...
    └── ...
```

## 🔧 Advanced Usage

### Custom FastAPI App Structure

```python
# main.py
from fastapi import FastAPI

# Custom app variable name
api = FastAPI(title="My API", version="1.0.0")

@api.get("/")
def read_root():
    return {"message": "Hello World"}
```

```bash
# Generate with custom app name
aemon generate -m main.py -a api
```

### Module Import Paths

```bash
# File path
aemon generate -m src/myapp/main.py

# Python import path
aemon generate -m myapp.main

# Relative paths
aemon generate -m ../other-project/main.py
```

### CI/CD Integration

```yaml
# .github/workflows/docs.yml
name: Generate API Documentation

on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install aemon
          pip install -r requirements.txt
      
      - name: Generate documentation
        run: aemon generate -m main.py
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## 🛠️ Development

### Prerequisites

- Python 3.12+
- FastAPI 0.115+
- PyYAML 6.0+

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/aemon.git
cd aemon

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check aemon
mypy aemon
```

### Project Structure

```
aemon/
├── cli/                    # CLI interface
├── config/                 # Configuration handling
├── core/                   # Core functionality
│   ├── exceptions.py       # Custom exceptions
│   ├── fast_api_loader.py  # FastAPI app loading
│   └── generator.py        # OpenAPI generation
├── output/                 # HTML generation
├── parser/                 # CLI argument parsing
└── assets/                 # Static assets
```

## 📝 Examples

### Basic FastAPI App

```python
# app.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="My API",
    description="A simple API example",
    version="1.0.0"
)

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/items/")
def create_item(item: Item):
    return {"item": item}
```

```bash
# Generate documentation
aemon generate -m app.py

# Start development server
aemon serve --open
```

### Advanced Configuration

```yaml
# aemon.yaml
aemon:
  output_dir: "documentation/api"
  title: "E-commerce API"
  description: "RESTful API for e-commerce platform"
  
  contact:
    name: "Development Team"
    url: "https://example.com/contact"
    email: "dev@example.com"
  
  license:
    name: "Apache 2.0"
    url: "https://www.apache.org/licenses/LICENSE-2.0.html"
  
  servers:
    - url: "https://api.example.com"
      description: "Production server"
    - url: "https://staging.example.com"
      description: "Staging server"
  
  swagger_ui_config:
    docExpansion: "list"
    defaultModelsExpandDepth: 2
    displayRequestDuration: true
    filter: true
    showExtensions: true
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [Swagger UI](https://swagger.io/tools/swagger-ui/) for the interactive documentation
- [PyYAML](https://pyyaml.org/) for YAML configuration support