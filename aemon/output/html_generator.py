import shutil
from pathlib import Path
from typing import Optional


class HTMLGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def ensure_assets(self):
        """Copy swagger-ui bundle."""
        assets_src = Path(__file__).parents[1] / "assets/swagger"
        assets_dst = self.output_dir.parent / "assets" 
        if not assets_dst.exists():
            shutil.copytree(assets_src, assets_dst)

    def update_index(self, new_version: Optional[str] = None):
        """Update index.html with new api versions"""
        if new_version:
            self.generate_version_page(self.output_dir / new_version)
        self.generate_html_index()

    def generate_html_index(self):
        """Create root index.html."""
        self.ensure_assets()
        versions = sorted(
            [d.name for d in self.output_dir.glob("v*") if d.is_dir()],
            key=lambda v: int(v[1:]) if v[1:].isdigit() else 0
        )
        rows = "\n".join(
            f"<tr><td><a href='api/{v}/index.html'>{v}</a></td></tr>"
            for v in versions
        )
        index_html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>API Versions</title>
    <style>
      body {{ font-family: Arial, sans-serif; padding: 40px; background: #f9f9f9; }}
      table {{ width: 50%; border-collapse: collapse; margin: auto; }}
      th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
      tr:hover {{ background-color: #f1f1f1; }}
      h1 {{ text-align: center; }}
    </style>
  </head>
  <body>
    <h1>API versions list</h1>
    <table>
      <tr><th>Version</th></tr>
      {rows}
    </table>
  </body>
</html>
"""
        index_path = self.output_dir.parent / "index.html"
        index_path.write_text(index_html, encoding="utf-8")

    def generate_version_page(self, version_dir: Path):
        """Create swagger-ui page."""
        version_html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>API {version_dir.name}</title>
    <link rel="stylesheet" type="text/css" href="../../assets/swagger-ui.css" />
    <link rel="icon" type="image/png" href="../../assets/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="../../assets/favicon-16x16.png" sizes="16x16" />
    <style>
      html {{ box-sizing: border-box; overflow-y: scroll; }}
      *, *:before, *:after {{ box-sizing: inherit; }}
      body {{ margin:0; background: #fafafa; }}
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
          deepLinking: true,
          presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
          ],
          plugins: [SwaggerUIBundle.plugins.DownloadUrl],
          layout: "StandaloneLayout"
        }});
        window.ui = ui;
      }};
    </script>
  </body>
</html>
"""
        version_dir.mkdir(parents=True, exist_ok=True)
        (version_dir / "index.html").write_text(version_html, encoding="utf-8")
