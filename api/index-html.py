from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Create a simple FastAPI app to serve HTML
app = FastAPI()

# Read index.html
_html_path = Path(__file__).parent.parent / "index.html"
_html_content = ""

if _html_path.exists():
    with open(_html_path, 'r', encoding='utf-8') as f:
        _html_content = f.read()

@app.get("/", response_class=HTMLResponse)
@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_html(path: str = ""):
    """Serve index.html for all routes"""
    if _html_content:
        return HTMLResponse(content=_html_content)
    else:
        return HTMLResponse(
            content="<h1>404 - index.html not found</h1>",
            status_code=404
        )

