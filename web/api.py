# web/api.py
from flask import request, jsonify
from state import RUNNING_TASKS, WEB_TASKS
from core.utils import gui_log
from core.utils import save_config, load_config
from web.auth import login_required

# IMPORTANT:
# We import the START logic later (Step 3)
# For now we just keep the route shell

@login_required
def stream_route():
    from state import WEB_LOGS
    return jsonify({
        "logs": list(WEB_LOGS),
        "tasks": list(WEB_TASKS.values())
    })

@login_required
def stop_route():
    RUNNING_TASKS.clear()
    WEB_TASKS.clear()
    gui_log("🛑 Stopped/Cleared Tasks", "err")
    return jsonify({"status": "ok"})
