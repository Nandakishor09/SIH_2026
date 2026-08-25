"""
Legal Metrology Compliance Checker - Launcher
Starts the FastAPI application and dev server on http://127.0.0.1:8000
"""

import uvicorn
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print("=================================================================")
    print("  Starting Legal Metrology Product Compliance Checker Server     ")
    print("  URL: http://127.0.0.1:8000                                     ")
    print("=================================================================")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
