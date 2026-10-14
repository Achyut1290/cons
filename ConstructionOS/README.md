# ConstructionOS

ConstructionOS is a Flask-based construction project management app for projects, tasks, materials, labour, expenses, site updates, analytics, and reports.

## Requirements
- Python 3.10+
- MySQL 8+
- Git (optional for deployment)

## Run locally (Windows PowerShell)
1. Open a terminal in the `ConstructionOS` folder.
2. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install packages:
   ```powershell
   pip install -r requirements.txt
   ```
4. Create a MySQL database and tables by running `database/schema.sql` in MySQL Workbench or the MySQL CLI.
5. Copy `.env.example` to `.env` and fill in your own MySQL credentials and a long random `FLASK_SECRET_KEY`. Do not commit `.env`.
6. Set the variables from `.env` in your terminal/session (or use a dotenv loader if you add `python-dotenv`), then run:
   ```powershell
   python app.py
   ```
7. Open `http://127.0.0.1:5000`.

Note: Flask does not automatically load `.env` with the current requirements. Either set the variables in PowerShell before starting, or install/use `python-dotenv`.

Example PowerShell variables:
```powershell
$env:FLASK_SECRET_KEY = "replace-with-a-long-random-secret"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
$env:MYSQL_USER = "your_mysql_user"
$env:MYSQL_PASSWORD = "your_mysql_password"
$env:MYSQL_DATABASE = "constructionos"
python app.py
```

## Deploy to Render
The Flask application is in the `ConstructionOS` subfolder.
- Create a Render **Web Service** connected to the GitHub repository.
- Set **Root Directory** to `ConstructionOS`.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add environment variables: `FLASK_SECRET_KEY`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE`.
- Set `COOKIE_SECURE=true` in production.
- Configure a hosted MySQL database and import `database/schema.sql` into it before using database-backed pages.
- Do not put credentials in source code or commit a `.env` file.

`/health` provides a database-independent health check.

## Important security notes
- Public registration always creates a `USER` account. Privileged roles must be assigned by an administrator through a controlled process.
- Configure SMTP environment variables (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_SENDER`) if password-reset emails are required. Without SMTP, reset links are written to application logs, which is only suitable for development.
