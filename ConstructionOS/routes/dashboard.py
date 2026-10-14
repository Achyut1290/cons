from flask import Blueprint, render_template

from config import get_db_connection
from routes.auth import role_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@role_required("ADMIN", "USER", "SITE_ENGINEER", "CHAIRMAN")
def dashboard():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM projects")
    projects = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks")
    tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM materials")
    materials = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses")
    expenses = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        projects=projects,
        tasks=tasks,
        materials=materials,
        expenses=expenses,
    )
