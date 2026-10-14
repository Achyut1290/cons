import os
import secrets

from flask import Flask, redirect, url_for
from flask_login import current_user

from routes.analytics import analytics_bp
from routes.auth import auth_bp, login_manager
from routes.dashboard import dashboard_bp
from routes.expenses import expenses_bp
from routes.labour import labour_bp
from routes.materials import materials_bp
from routes.projects import projects_bp
from routes.reports import reports_bp
from routes.site_updates import site_updates_bp
from routes.tasks import tasks_bp

app = Flask(__name__)
# Set FLASK_SECRET_KEY in production so sessions remain valid across restarts.
# The generated fallback is suitable only for local development.
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true",
)
app.config["LOGIN_MESSAGE"] = "Please log in to continue."

login_manager.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(materials_bp)
app.register_blueprint(labour_bp)
app.register_blueprint(expenses_bp)
app.register_blueprint(site_updates_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(reports_bp)


@app.route("/health")
def health():
    """Lightweight deployment health check; does not require a database."""
    return {"status": "ok", "service": "ConstructionOS"}, 200


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
