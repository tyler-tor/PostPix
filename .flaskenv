# Non-secret settings for the `flask` command (loaded by python-dotenv).
# This file IS committed. Secrets belong in .env (git-ignored), which wins over it.
FLASK_APP=app
# Port for `flask run` (Flask's default 5000 is taken by AirPlay on macOS).
# Same as gunicorn's local default and the Vite proxy target.
FLASK_RUN_PORT=8000
