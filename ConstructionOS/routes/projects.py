from flask import Blueprint, redirect, render_template, request

from config import get_db_connection
from routes.auth import role_required


projects_bp = Blueprint("projects", __name__, url_prefix="/projects")


@projects_bp.route("/")
@role_required("ADMIN", "USER", "SITE_ENGINEER", "CHAIRMAN")
def list_projects():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("projects/list.html", projects=projects)


@projects_bp.route("/add", methods=["GET", "POST"])
@role_required("ADMIN", "SITE_ENGINEER")
def add_project():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]
        budget = request.form["budget"]
        status = request.form["status"]

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO projects (
                name, description, location, start_date, end_date, budget, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (name, description, location, start_date, end_date, budget, status),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect("/projects/")

    return render_template("projects/add.html")
