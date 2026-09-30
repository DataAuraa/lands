"""
Start script for development: adds project root and ml/ to sys.path
so `from app.xxx` works from backend/ AND `from ml.xxx` resolves from root.
"""
import sys
import os

# Add the project root (landslide-ai-ner) to path so 'ml' module resolves
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir  = os.path.join(project_root, 'backend')

sys.path.insert(0, project_root)   # for ml/, simulation/
sys.path.insert(0, backend_dir)    # for app/ (FastAPI app)

# Now import and run uvicorn
import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[backend_dir, project_root],
    )
