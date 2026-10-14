from flask import Blueprint, redirect, render_template, request

from config import get_db_connection
from routes.auth import role_required

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")


@expenses_bp.route("/")
@role_required("ADMIN", "USER", "SITE_ENGINEER", "CHAIRMAN")
def list_expenses():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
    expenses = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("expenses/list.html", expenses=expenses)


@expenses_bp.route("/add", methods=["GET", "POST"])
@role_required("ADMIN", "SITE_ENGINEER")
def add_expense():
    if request.method == "POST":
        project_id = request.form["project_id"]
        category = request.form["category"]
        description = request.form["description"]
        amount = request.form["amount"]
        expense_date = request.form["expense_date"]

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO expenses (project_id, category, description, amount, expense_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (project_id, category, description, amount, expense_date),
        )
        connection.commit()
        cursor.close()
        connection.close()
        return redirect("/expenses/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM projects")
    projects = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template("expenses/add.html", projects=projects)
