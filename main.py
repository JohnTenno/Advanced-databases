"""Development entry point.

Usage:  .venv\\Scripts\\python.exe main.py
Then open http://127.0.0.1:5000
"""
from app import create_app

application = create_app()

if __name__ == "__main__":
    target = application.config["APP_CONFIG"].db_target
    print(f"Blog BDA - connecting to {target}")
    print("Open http://127.0.0.1:5000")
    application.run(debug=True)
