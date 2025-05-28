import logging
from pathlib import Path


class HTMLGenerator:
    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.index_file = self.output_dir / "index.html"

    def update_index(self, new_version: str | None = None) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        versions = sorted([
            d.name for d in self.output_dir.glob("v*")
            if d.is_dir() and d.name[1:].isdigit()
        ])

        html = self._render_html(versions)
        self.index_file.write_text(html, encoding="utf-8")
        logging.info(f"Обновлён HTML-обзор версий: {self.index_file}")

    def _render_html(self, versions: list[str]) -> str:
        rows = []
        for v in versions:
            rows.append(f"""
            <div class="version">
                <div class="version-title">
                    <a href="{v}/openapi.json">{v}</a>
                </div>
                <div class="description"></div>
            </div>
            """)
        versions_html = "\n".join(rows)

        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Документация API</title>
    <style>
        body {{
            font-family: system-ui, sans-serif;
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
            color: #333;
        }}
        h1 {{
            text-align: center;
        }}
        .version {{
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        .version-title {{
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }}
        .description {{
            font-size: 0.95rem;
            color: #555;
        }}
        a {{
            text-decoration: none;
            color: #0066cc;
        }}
    </style>
</head>
<body>
    <h1>Документация API</h1>
    {versions_html}
</body>
</html>"""