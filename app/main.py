import importlib.util
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Dynamically load backend/app/main.py
backend_main_path = os.path.join(backend_dir, "app", "main.py")
spec = importlib.util.spec_from_file_location("backend_main_module", backend_main_path)
backend_module = importlib.util.module_from_spec(spec)
sys.modules["backend_main_module"] = backend_module
spec.loader.exec_module(backend_module)

app = backend_module.app
