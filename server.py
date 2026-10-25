from pathlib import Path
from fastapi.staticfiles import StaticFiles
from backend.app import app

public = Path(__file__).parent / 'public'
if public.exists():
    app.mount('/', StaticFiles(directory=public, html=True), name='frontend')
