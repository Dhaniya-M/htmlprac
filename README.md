# Flask Backend for htmlprac

This folder contains a Flask backend that mirrors the existing PHP backend features for the htmlprac project. The frontend remains unchanged and will call these API endpoints under `/api/*`.

Key features implemented:
- Authentication (register/login) with JWT via `flask-jwt-extended` and password hashing using `flask-bcrypt`.
- Modular Blueprints for `auth`, `chatbot`, `market`, `soil`, `weather`, `pest`.
- MySQL connection pooling via `mysql-connector-python`.
- CORS enabled for frontend requests.

Quick start (local):

1. Create a virtualenv and install requirements

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Configure environment variables (example):

```powershell
$env:MYSQL_HOST='localhost'; $env:MYSQL_USER='root'; $env:MYSQL_PASSWORD=''; $env:MYSQL_DB='agri_db'; $env:JWT_SECRET_KEY='change-me'
```

3. Run app

```powershell
python app.py
```

Notes:
- Create required MySQL tables (users, market_info, soil_tests, pest_reports) before using the DB-backed endpoints or rely on mock fallbacks.
- The AI and pest detection endpoints are placeholders for future integration.
