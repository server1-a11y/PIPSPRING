from flask import Flask, render_template_string
from config import PORT, SECRET_KEY
from web.auth import login_route, logout_route, login_required
from web.api import stream_route, stop_route
from web.start import start_route
from core.utils import load_config
from web.ui import HTML_TEMPLATE

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route("/login", methods=["GET", "POST"])
def login():
    return login_route()

@app.route("/logout")
def logout():
    return logout_route()

@app.route("/")
@login_required
def index():
    config = load_config()
    return render_template_string(
        HTML_TEMPLATE,
        page="dashboard",
        config=config
    )

@app.route("/api/start", methods=["POST"])
@login_required
def api_start():
    return start_route()

@app.route("/api/stream")
@login_required
def api_stream():
    return stream_route()

@app.route("/api/stop", methods=["POST"])
@login_required
def api_stop():
    return stop_route()

if __name__ == "__main__":
    print(f"Server running on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
