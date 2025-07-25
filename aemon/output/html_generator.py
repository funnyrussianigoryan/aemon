"""Enhanced HTML generator with modern UI, themes and advanced features."""
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from aemon.core.exceptions import GenerationError


class HTMLGenerator:
    """Enhanced HTML generator with modern UI and advanced features."""
    
    def __init__(self, output_dir: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize HTML generator.
        
        Args:
            output_dir: Output directory for generated files
            config: Configuration dictionary for customization
        """
        self.output_dir = output_dir
        self.config = config or {}

    def ensure_assets(self) -> None:
        """Copy swagger-ui bundle and custom assets."""
        assets_src = Path(__file__).parents[1] / "assets/swagger"
        assets_dst = self.output_dir.parent / "assets" 
        
        if not assets_dst.exists():
            try:
                shutil.copytree(assets_src, assets_dst)
            except Exception as e:
                raise GenerationError(f"Failed to copy assets: {e}") from e

    def update_index(self, new_version: Optional[str] = None) -> None:
        """Update index.html with new api versions."""
        if new_version:
            self.generate_version_page(self.output_dir / new_version)
        self.generate_html_index()

    def generate_html_index(self) -> None:
        """Create modern root index.html with search and filtering."""
        self.ensure_assets()
        
        versions = self._get_versions_with_metadata()
        
        # Generate version rows
        rows = ""
        for version_info in versions:
            version = version_info["version"]
            metadata = version_info.get("metadata", {})
            generated_at = metadata.get("generated_at", "Unknown")
            routes_count = metadata.get("routes_count", "Unknown")
            
            # Format date
            try:
                if generated_at != "Unknown":
                    dt = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    formatted_date = "Unknown"
            except:
                formatted_date = generated_at
            
            rows += f"""
            <tr data-version="{version}" data-date="{generated_at}">
                <td>
                    <a href="api/{version}/index.html" class="version-link">
                        <span class="version-badge">{version}</span>
                    </a>
                </td>
                <td class="date-cell">{formatted_date}</td>
                <td class="routes-cell">{routes_count}</td>
                <td class="actions-cell">
                    <a href="api/{version}/api_config.yaml" class="action-link" title="Download YAML">
                        📄 YAML
                    </a>
                    <a href="api/{version}/api_config.json" class="action-link" title="Download JSON">
                        📄 JSON
                    </a>
                </td>
            </tr>
            """
        
        title = self.config.get("title", "API Documentation")
        description = self.config.get("description", "API versions and documentation")
        
        index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --primary-hover: #1d4ed8;
            --background: #ffffff;
            --surface: #f8fafc;
            --surface-hover: #f1f5f9;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border: #e2e8f0;
            --border-hover: #cbd5e1;
            --success: #059669;
            --warning: #d97706;
            --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        }}
        
        [data-theme="dark"] {{
            --background: #0f172a;
            --surface: #1e293b;
            --surface-hover: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --border: #334155;
            --border-hover: #475569;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--background);
            color: var(--text-primary);
            line-height: 1.6;
            transition: all 0.3s ease;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, var(--primary-color), #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        
        .controls {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
        }}
        
        .search-container {{
            display: flex;
            gap: 1rem;
            flex: 1;
            min-width: 300px;
        }}
        
        .search-input {{
            flex: 1;
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            background: var(--surface);
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.2s;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgb(37 99 235 / 0.1);
        }}
        
        .theme-toggle {{
            padding: 0.75rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.2s;
        }}
        
        .theme-toggle:hover {{
            background: var(--surface-hover);
            border-color: var(--border-hover);
        }}
        
        .table-container {{
            background: var(--surface);
            border-radius: 0.75rem;
            box-shadow: var(--shadow);
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: var(--primary-color);
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        td {{
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            transition: all 0.2s;
        }}
        
        tr:hover td {{
            background: var(--surface-hover);
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .version-link {{
            text-decoration: none;
            color: inherit;
            display: block;
            transition: all 0.2s;
        }}
        
        .version-badge {{
            display: inline-block;
            background: var(--primary-color);
            color: white;
            padding: 0.375rem 0.75rem;
            border-radius: 0.375rem;
            font-weight: 600;
            font-size: 0.875rem;
            transition: all 0.2s;
        }}
        
        .version-link:hover .version-badge {{
            background: var(--primary-hover);
            transform: translateY(-1px);
            box-shadow: var(--shadow-lg);
        }}
        
        .date-cell {{
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        
        .routes-cell {{
            font-weight: 600;
            color: var(--success);
        }}
        
        .actions-cell {{
            display: flex;
            gap: 0.5rem;
        }}
        
        .action-link {{
            text-decoration: none;
            color: var(--text-secondary);
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            border: 1px solid var(--border);
            transition: all 0.2s;
        }}
        
        .action-link:hover {{
            color: var(--primary-color);
            border-color: var(--primary-color);
            background: var(--surface-hover);
        }}
        
        .empty-state {{
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
        }}
        
        .empty-state h3 {{
            margin-bottom: 0.5rem;
            color: var(--text-primary);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .controls {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .search-container {{
                min-width: auto;
            }}
            
            .actions-cell {{
                flex-direction: column;
            }}
            
            th, td {{
                padding: 0.75rem 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{title}</h1>
            <p>{description}</p>
        </header>
        
        <div class="controls">
            <div class="search-container">
                <input 
                    type="text" 
                    id="searchInput" 
                    class="search-input" 
                    placeholder="Search versions..."
                >
            </div>
            <button class="theme-toggle" id="themeToggle" title="Toggle theme">
                🌙
            </button>
        </div>
        
        <div class="table-container">
            <table id="versionsTable">
                <thead>
                    <tr>
                        <th>Version</th>
                        <th>Generated</th>
                        <th>Routes</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {rows if rows.strip() else '<tr><td colspan="4" class="empty-state"><h3>No API versions found</h3><p>Generate your first API documentation to see it here.</p></td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        const body = document.body;
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        body.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
        
        themeToggle.addEventListener('click', () => {{
            const currentTheme = body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        }});
        
        function updateThemeIcon(theme) {{
            themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        }}
        
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const table = document.getElementById('versionsTable');
        const rows = table.querySelectorAll('tbody tr');
        
        searchInput.addEventListener('input', (e) => {{
            const searchTerm = e.target.value.toLowerCase();
            
            rows.forEach(row => {{
                const version = row.getAttribute('data-version') || '';
                const text = row.textContent.toLowerCase();
                
                if (version.toLowerCase().includes(searchTerm) || text.includes(searchTerm)) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }});
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (e.ctrlKey || e.metaKey) {{
                if (e.key === 'k') {{
                    e.preventDefault();
                    searchInput.focus();
                }}
                if (e.key === 'd') {{
                    e.preventDefault();
                    themeToggle.click();
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        index_path = self.output_dir.parent / "index.html"
        try:
            index_path.write_text(index_html, encoding="utf-8")
        except Exception as e:
            raise GenerationError(f"Failed to generate index.html: {e}") from e

    def generate_version_page(self, version_dir: Path) -> None:
        """Create enhanced swagger-ui page with custom configuration."""
        swagger_config = self.config.get("swagger_ui_config", {})
        
        # Default Swagger UI configuration
        default_config = {
            "deepLinking": True,
            "displayRequestDuration": True,
            "docExpansion": "none",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "tryItOutEnabled": True,
            "requestSnippetsEnabled": True,
            "supportedSubmitMethods": ["get", "post", "put", "delete", "patch", "head", "options"],
        }
        
        # Merge configurations
        final_config = {**default_config, **swagger_config}
        config_json = json.dumps(final_config, indent=2)
        
        version_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API {version_dir.name}</title>
    <link rel="stylesheet" type="text/css" href="../../assets/swagger-ui.css" />
    <link rel="icon" type="image/png" href="../../assets/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="../../assets/favicon-16x16.png" sizes="16x16" />
    <style>
        html {{ 
            box-sizing: border-box; 
            overflow-y: scroll; 
        }}
        *, *:before, *:after {{ 
            box-sizing: inherit; 
        }}
        body {{ 
            margin: 0; 
            background: #fafafa; 
        }}
        
        .swagger-ui .topbar {{
            background-color: #2563eb;
            border-bottom: 1px solid #1d4ed8;
        }}
        
        .swagger-ui .topbar .download-url-wrapper {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .back-link {{
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            background: rgba(255, 255, 255, 0.1);
            transition: all 0.2s;
            font-weight: 500;
        }}
        
        .back-link:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }}
        
        /* Dark theme support */
        @media (prefers-color-scheme: dark) {{
            body {{
                background: #1a1a1a;
            }}
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    
    <script src="../../assets/swagger-ui-bundle.js"></script>
    <script src="../../assets/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "api_config.yaml",
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [SwaggerUIBundle.plugins.DownloadUrl],
                layout: "StandaloneLayout",
                ...{config_json}
            }});
            
            window.ui = ui;
            
            // Add back link to topbar
            setTimeout(() => {{
                const topbar = document.querySelector('.swagger-ui .topbar');
                if (topbar) {{
                    const backLink = document.createElement('a');
                    backLink.href = '../../index.html';
                    backLink.className = 'back-link';
                    backLink.textContent = '← Back to versions';
                    
                    const downloadWrapper = topbar.querySelector('.download-url-wrapper');
                    if (downloadWrapper) {{
                        downloadWrapper.appendChild(backLink);
                    }}
                }}
            }}, 100);
        }};
    </script>
</body>
</html>"""
        
        try:
            version_dir.mkdir(parents=True, exist_ok=True)
            (version_dir / "index.html").write_text(version_html, encoding="utf-8")
        except Exception as e:
            raise GenerationError(f"Failed to generate version page: {e}") from e

    def _get_versions_with_metadata(self) -> List[Dict[str, Any]]:
        """Get versions with their metadata sorted by version number."""
        if not self.output_dir.exists():
            return []
            
        versions = []
        for version_dir in self.output_dir.glob("v*"):
            if not version_dir.is_dir():
                continue
                
            version_info = {"version": version_dir.name}
            
            # Load metadata if available
            metadata_path = version_dir / "metadata.json"
            if metadata_path.exists():
                try:
                    with metadata_path.open("r", encoding="utf-8") as f:
                        version_info["metadata"] = json.load(f)
                except Exception:
                    pass  # Skip if metadata can't be loaded
                    
            versions.append(version_info)
        
        # Sort by version number (extract number from version string)
        def version_sort_key(v):
            version = v["version"]
            try:
                # Extract number from version (e.g., "v1" -> 1)
                return int(version[1:]) if version[1:].isdigit() else 0
            except:
                return 0
                
        return sorted(versions, key=version_sort_key, reverse=True)

    def generate_comparison_page(self, versions: List[str]) -> None:
        """Generate a comparison page between different API versions."""
        # This would be a future enhancement for comparing API versions
        pass
