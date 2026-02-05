from flask import session, redirect, url_for, render_template_string, request
from functools import wraps
from config import WEB_PASSWORD
from web.ui import HTML_TEMPLATE

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def login_route():
    if request.method == "POST":
        if request.form.get("password") == WEB_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        return render_template_string(
            HTML_TEMPLATE,
            page="login",
            error="Invalid password"
        )

    return render_template_string(
        HTML_TEMPLATE,
        page="login",
        error=None
    )

def logout_route():
    session.pop("logged_in", None)
    return redirect(url_for("login"))
