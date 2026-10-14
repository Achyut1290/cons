from flask import Blueprint, redirect, render_template, request

from config import get_db_connection
from routes.auth import role_required

site_updates_bp = Blueprint("site_updates", __name__, url_prefix="/site-updates")


@site_updates_bp.route("/")
@role_required("ADMIN", "USER", "SITE_ENGINEER", "CHAIRMAN")
def list_updates():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM site_updates ORDER BY id DESC")
    updates = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("site_updates/list.html", updates=updates)


@site_updates_bp.route("/add", methods=["GET", "POST"])
@role_required("ADMIN", "SITE_ENGINEER")
def add_update():
    if request.method == "POST":
        project_id = request.form["project_id"]
        update_date = request.form["update_date"]
        description = request.form["description"]
        progress = request.form["progress"]
        issues = request.form["issues"]

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO site_updates (project_id, update_date, description, progress, issues)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (project_id, update_date, description, progress, issues),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect("/site-updates/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM projects")
    projects = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("site_updates/add.html", projects=projects)
