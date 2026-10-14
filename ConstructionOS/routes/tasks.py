from flask import Blueprint, redirect, render_template, request

from config import get_db_connection
from routes.auth import role_required


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/")
@role_required("ADMIN", "USER", "SITE_ENGINEER", "CHAIRMAN")
def list_tasks():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("tasks/list.html", tasks=tasks)


@tasks_bp.route("/add", methods=["GET", "POST"])
@role_required("ADMIN", "SITE_ENGINEER")
def add_task():
    if request.method == "POST":
        project_id = request.form["project_id"]
        title = request.form["title"]
        description = request.form["description"]
        assigned_to = request.form["assigned_to"]
        start_date = request.form["start_date"]
        due_date = request.form["due_date"]
        status = request.form["status"]
        priority = request.form["priority"]

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (
                project_id, title, description, assigned_to, start_date, due_date, status, priority
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (project_id, title, description, assigned_to, start_date, due_date, status, priority),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect("/tasks/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM projects")
    projects = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("tasks/add.html", projects=projects)
