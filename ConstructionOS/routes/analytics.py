from datetime import date

from flask import Blueprint, render_template

from config import get_db_connection
from routes.auth import role_required

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/")
@role_required("ADMIN", "USER", "SITE_ENGINEER", "CHAIRMAN")
def analytics_dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM projects")
    total_projects = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM tasks")
    total_tasks = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM tasks WHERE status = 'Completed'")
    completed_tasks = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM tasks WHERE status = 'Pending'")
    pending_tasks = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM tasks WHERE status = 'Delayed' OR (due_date < %s AND status != 'Completed')", (date.today(),))
    delayed_tasks = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(budget), 0) AS total FROM projects")
    total_budget = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses")
    total_expense = cursor.fetchone()["total"]

    cursor.execute("SELECT * FROM materials WHERE quantity < minimum_stock ORDER BY quantity ASC")
    low_stock_materials = cursor.fetchall()

    cursor.execute("SELECT AVG(progress) AS avg_progress FROM site_updates")
    avg_progress = cursor.fetchone()["avg_progress"] or 0

    cursor.execute("SELECT * FROM tasks WHERE due_date < %s AND status != 'Completed' ORDER BY due_date ASC LIMIT 5", (date.today(),))
    overdue_tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    project_budget_warning = total_expense > (total_budget * 0.8)
    schedule_status = "On Track" if avg_progress >= 70 else "Behind Schedule"

    return render_template(
        "analytics.html",
        total_projects=total_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        delayed_tasks=delayed_tasks,
        total_budget=total_budget,
        total_expense=total_expense,
        low_stock_materials=low_stock_materials,
        avg_progress=avg_progress,
        overdue_tasks=overdue_tasks,
        project_budget_warning=project_budget_warning,
        schedule_status=schedule_status,
    )
