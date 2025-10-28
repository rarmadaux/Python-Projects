from flask import Flask, request, jsonify, render_template
import subprocess
import platform
import importlib
import os, json


# --- Detect OS ----------------------------------------------------
os_name = platform.system().lower()

print(f"Detected OS: {os_name}")

if os_name == "linux":
    audio_module = importlib.import_module("audio_linux")
elif os_name == "windows":
    audio_module = importlib.import_module("audio_windows")
else:
    raise SystemExit(" Unsupported OS — only Linux and Windows supported.")

# --- Flask App ----------------------------------------------------
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/list_audio_apps")
def list_audio_apps():
    apps = audio_module.get_active_audio_apps()
    return jsonify(apps)

@app.route("/list_available_apps")
def list_available_apps():
    """Return all apps configured in apps.json for the web interface."""
    import json, os

    config_path = os.path.join("config", "apps.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            app_map = json.load(f)
        # Return as a simple list of app names
        return jsonify(list(app_map.keys()))
    else:
        return jsonify([])


@app.route("/open_app", methods=["POST"])
def open_app():
    data = request.get_json()
    app_name = data.get("app")

    if not app_name:
        return jsonify({"error": "No app specified"}), 400

    # Optional: resolve from apps.json if it exists
    config_path = os.path.join("config", "apps.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            apps = json.load(f)
        if app_name in apps:
            app_name = apps[app_name]

    try:
        if os_name == "windows":
            if os.path.exists(app_name):
                # Use list form (no shell) for full paths
                subprocess.Popen([app_name], shell=False)
            else:
                # Fallback to "start" for PATH commands
                subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=True)
        else:
            # Linux / Mac
            subprocess.Popen(app_name, shell=True)

        print(f" Opened app: {app_name}")
        return jsonify({"status": "ok", "message": f"Opened {app_name}"}), 200

    except Exception as e:
        print(f"[ERROR] Failed to open app: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/set_volume", methods=["POST"])
def set_volume():
    data = request.get_json()
    app_name = data.get("app")
    volume = data.get("volume")

    if app_name is None or volume is None:
        return jsonify({"error": "app and volume required"}), 400

    success = audio_module.set_app_volume(app_name, float(volume))

    return jsonify({"status": "ok" if success else "not_found"}), 200 if success else 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
