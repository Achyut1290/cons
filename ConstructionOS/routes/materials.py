from flask import Blueprint, redirect, render_template, request

from config import get_db_connection
from routes.auth import role_required

materials_bp = Blueprint("materials", __name__, url_prefix="/materials")


@materials_bp.route("/")
@role_required("ADMIN", "USER", "SITE_ENGINEER", "CHAIRMAN")
def list_materials():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM materials ORDER BY id DESC")
    materials = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("materials/list.html", materials=materials)


@materials_bp.route("/add", methods=["GET", "POST"])
@role_required("ADMIN", "SITE_ENGINEER")
def add_material():
    if request.method == "POST":
        project_id = request.form["project_id"]
        name = request.form["name"]
        category = request.form["category"]
        quantity = request.form["quantity"]
        unit = request.form["unit"]
        minimum_stock = request.form["minimum_stock"]
        cost = request.form["cost"]

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO materials (project_id, name, category, quantity, unit, minimum_stock, cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (project_id, name, category, quantity, unit, minimum_stock, cost),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect("/materials/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM projects")
    projects = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("materials/add.html", projects=projects)
