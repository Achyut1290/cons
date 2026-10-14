from flask import Blueprint, render_template

from config import get_db_connection
from routes.auth import role_required

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/")
@role_required("ADMIN", "USER", "SITE_ENGINEER", "CHAIRMAN")
def project_reports():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT p.id, p.name, p.status, p.budget,
               COALESCE(SUM(e.amount), 0) AS spent,
               COALESCE(AVG(s.progress), 0) AS progress
        FROM projects p
        LEFT JOIN expenses e ON e.project_id = p.id
        LEFT JOIN site_updates s ON s.project_id = p.id
        GROUP BY p.id, p.name, p.status, p.budget
        ORDER BY p.id DESC
        """
    )
    project_summary = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total FROM tasks WHERE status = 'Completed'")
    completed_tasks = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM tasks WHERE status != 'Completed'")
    open_tasks = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses")
    total_expense = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM materials WHERE quantity < minimum_stock")
    low_stock_count = cursor.fetchone()["total"]

    cursor.close()
    connection.close()

    return render_template(
        "reports.html",
        project_summary=project_summary,
        completed_tasks=completed_tasks,
        open_tasks=open_tasks,
        total_expense=total_expense,
        low_stock_count=low_stock_count,
    )
