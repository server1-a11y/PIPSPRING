from flask import Flask, render_template_string, jsonify, request, session
from config import PORT, SECRET_KEY
from web.auth import login_route, logout_route, login_required
from web.start import start_route
from state import RUNNING_TASKS, WEB_TASKS, WEB_LOGS
from core.utils import load_config, gui_log
from web.ui import HTML_TEMPLATE

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route("/login", methods=["GET", "POST"])
def login(): return login_route()

@app.route("/logout")
def logout(): return logout_route()

@app.route("/")
@login_required
def index():
    return render_template_string(HTML_TEMPLATE, page="dashboard", config=load_config())

@app.route("/api/start", methods=["POST"])
@login_required
def api_start(): return start_route()

@app.route("/api/stream")
@login_required
def api_stream():
    return jsonify({"logs": list(WEB_LOGS), "tasks": list(WEB_TASKS.values())})

@app.route("/api/stop", methods=["POST"])
@login_required
def api_stop():
    RUNNING_TASKS.clear()
    WEB_TASKS.clear()
    gui_log("🛑 Semua tugas dihentikan", "err")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
