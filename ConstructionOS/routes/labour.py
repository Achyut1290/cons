from flask import Blueprint, redirect, render_template, request

from config import get_db_connection
from routes.auth import role_required

labour_bp = Blueprint("labour", __name__, url_prefix="/labour")


@labour_bp.route("/")
@role_required("ADMIN", "USER", "SITE_ENGINEER", "CHAIRMAN")
def list_labour():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM labour ORDER BY id DESC")
    labour = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("labour/list.html", labour=labour)


@labour_bp.route("/add", methods=["GET", "POST"])
@role_required("ADMIN", "SITE_ENGINEER")
def add_labour():
    if request.method == "POST":
        project_id = request.form["project_id"]
        name = request.form["name"]
        worker_type = request.form["worker_type"]
        phone = request.form["phone"]
        daily_wage = request.form["daily_wage"]
        working_days = request.form["working_days"]

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO labour (project_id, name, worker_type, phone, daily_wage, working_days)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (project_id, name, worker_type, phone, daily_wage, working_days),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect("/labour/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM projects")
    projects = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("labour/add.html", projects=projects)
