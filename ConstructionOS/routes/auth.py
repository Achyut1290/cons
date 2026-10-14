from functools import wraps
from email.message import EmailMessage
import logging
import os
import smtplib

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash

from config import get_db_connection
from models.user import User

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to continue."


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to continue.")
                return redirect(url_for("auth.login"))
            if current_user.role not in allowed_roles:
                flash("You do not have permission to access this page.")
                return redirect(url_for("dashboard.dashboard"))
            return view_func(*args, **kwargs)
        return wrapper
    return decorator


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


def _password_reset_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="password-reset")


def _send_password_reset_email(email, reset_url):
    smtp_host = os.getenv("SMTP_HOST")
    if not smtp_host:
        current_app.logger.warning("Password reset link for %s: %s", email, reset_url)
        return

    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_SENDER") or smtp_username
    if not sender:
        raise RuntimeError("Set SMTP_SENDER or SMTP_USERNAME to send reset emails.")

    message = EmailMessage()
    message["Subject"] = "Reset your ConstructionOS password"
    message["From"] = sender
    message["To"] = email
    message.set_content(
        "Use the following link to reset your ConstructionOS password. "
        "The link expires in 30 minutes.\n\n"
        f"{reset_url}\n"
    )

    if smtp_port == 465:
        smtp_connection = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
    else:
        smtp_connection = smtplib.SMTP(smtp_host, smtp_port, timeout=10)

    with smtp_connection as smtp:
        if smtp_port != 465 and os.getenv("SMTP_USE_TLS", "true").lower() == "true":
            smtp.starttls()
        if smtp_username and smtp_password:
            smtp.login(smtp_username, smtp_password)
        smtp.send_message(message)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        # Public registration must not allow users to grant themselves privileged roles.\n        role = "USER"

        if not name or not email or not password:
            flash("Please fill in all fields.")
            return render_template("register.html")

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("User already exists.")
                cursor.close()
                connection.close()
                return render_template("register.html")

            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (name, email, hashed_password, role),
            )
            connection.commit()
            cursor.close()
            connection.close()
            flash("Registration successful! Please login.")
            return redirect("/login")
        except Exception:
            current_app.logger.exception("Registration failed.")
            flash("Registration is temporarily unavailable. Please check the database configuration and try again.")
            return render_template("register.html"), 503

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        connection = None
        cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
        except Exception:
            current_app.logger.exception("Unable to authenticate user.")
            flash("Login is temporarily unavailable. Please check the database configuration and try again.")
            return render_template("login.html"), 503
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        if row and check_password_hash(row["password"], password):
            user = User(
                user_id=row["id"],
                name=row["name"],
                email=row["email"],
                role=row.get("role", "USER"),
            )
            login_user(user)
            flash("Login successful.")
            return redirect("/dashboard")

        flash("Invalid email or password.")
        return render_template("login.html")

    return render_template("login.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if email:
            connection = None
            cursor = None
            try:
                connection = get_db_connection()
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT id, email, password FROM users WHERE email = %s",
                    (email,),
                )
                user = cursor.fetchone()
                if user:
                    token = _password_reset_serializer().dumps(
                        {"user_id": user["id"], "password_hash": user["password"]}
                    )
                    reset_url = url_for(
                        "auth.reset_password", token=token, _external=True
                    )
                    _send_password_reset_email(user["email"], reset_url)
            except Exception:
                current_app.logger.exception("Unable to process password reset request.")
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()

        flash("If an account matches that email, reset instructions have been sent.")
        return redirect(url_for("auth.forgot_password"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        payload = _password_reset_serializer().loads(token, max_age=1800)
    except (BadSignature, SignatureExpired):
        flash("That password reset link is invalid or has expired.")
        return redirect(url_for("auth.forgot_password"))

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, password FROM users WHERE id = %s",
            (payload.get("user_id"),),
        )
        user = cursor.fetchone()
        if not user or user["password"] != payload.get("password_hash"):
            flash("That password reset link is invalid or has expired.")
            return redirect(url_for("auth.forgot_password"))

        if request.method == "POST":
            password = request.form.get("password", "")
            confirmation = request.form.get("confirm_password", "")
            if len(password) < 8:
                flash("Choose a password with at least 8 characters.")
            elif password != confirmation:
                flash("The passwords do not match.")
            else:
                cursor.execute(
                    "UPDATE users SET password = %s WHERE id = %s AND password = %s",
                    (
                        generate_password_hash(password),
                        user["id"],
                        payload["password_hash"],
                    ),
                )
                connection.commit()
                flash("Your password has been changed. Please sign in.")
                return redirect(url_for("auth.login"))
    except Exception:
        current_app.logger.exception("Unable to reset password.")
        flash("Unable to reset your password right now. Please try again.")
        return redirect(url_for("auth.forgot_password"))
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template("reset_password.html", token=token)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))
