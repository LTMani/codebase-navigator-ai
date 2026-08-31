import os
from app import create_app

env_name = os.getenv("APP_ENV", "development")
app = create_app(env_name)

if __name__ == "__main__":
    host = app.config.get("HOST", "127.0.0.1")
    port = app.config.get("PORT", 5000)
    debug = app.config.get("DEBUG", True)
    print(f"Starting {app.config['APP_NAME']} on http://{host}:{port} ({env_name} mode)...")
    app.run(host=host, port=port, debug=debug)
