"""Dev server launcher that bypasses venv pyvenv.cfg (sandbox workaround)."""
import sys
import os

# Add venv site-packages to path so system Python can find all dependencies
venv_site = os.path.join(
    os.path.dirname(__file__), ".venv", "lib", "python3.12", "site-packages"
)
sys.path.insert(0, venv_site)

# Ensure the backend directory is in the path for app imports
backend_dir = os.path.dirname(__file__)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.chdir(backend_dir)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True, host="0.0.0.0", port=8001)
