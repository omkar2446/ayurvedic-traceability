import os
import sys

# Ensure backend root directory is at top priority in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir in sys.path:
    sys.path.remove(backend_dir)
sys.path.insert(0, backend_dir)

# Clear top-level 'app' module cache entries so imports inside backend/app load from backend/app
for mod in list(sys.modules.keys()):
    if mod == "app" or mod.startswith("app."):
        del sys.modules[mod]

# Import FastAPI app instance from backend/app/main.py
import app.main as _backend_main  # noqa: E402

app = _backend_main.app

