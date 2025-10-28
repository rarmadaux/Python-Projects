from flask import Flask, request, jsonify, render_template
import subprocess
import platform
import importlib
import os, json, webbrowser

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

# --- Helper: open URL locally ------------------------------------
def open_url_locally(url: str) -> bool:
    """Open a URL on the host machine running this Flask app."""
    try:
        if os_name == "windows":
            os.startfile(url)  # type: ignore[attr-defined]
        elif os_name == "darwin":  # macOS
            subprocess.Popen(["open", url])
        else:  # Linux
            subprocess.Popen(["xdg-open", url])
        return True
    except Exception:
        try:
            webbrowser.open(url, new=2)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to open link: {e}")
            return False

# --- Routes -------------------------------------------------------
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
    config_path = os.path.join("config", "apps.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            app_map = json.load(f)
        return jsonify(list(app_map.keys()))
    return jsonify([])

@app.route("/open_app", methods=["POST"])
def open_app():
    data = request.get_json()
    app_name = data.get("app")

    if not app_name:
        return jsonify({"error": "No app specified"}), 400

    config_path = os.path.join("config", "apps.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            apps = json.load(f)
        if app_name in apps:
            app_name = apps[app_name]

    try:
        if os_name == "windows":
            if os.path.exists(app_name):
                subprocess.Popen([app_name], shell=False)
            else:
                subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=True)
        else:
            subprocess.Popen(app_name, shell=True)

        print(f"Opened app: {app_name}")
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

@app.route("/list_links")
def list_links():
    """Return all web links configured in links.json."""
    links_path = os.path.join("config", "links.json")
    if os.path.exists(links_path):
        with open(links_path, "r") as f:
            links = json.load(f)
        return jsonify(links)
    return jsonify({})

@app.route("/open_link", methods=["POST"])
def open_link():
    """Open a link on the host machine (server side)."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    raw_url = data.get("url")

    links_path = os.path.join("config", "links.json")
    links = {}
    if os.path.exists(links_path):
        with open(links_path, "r") as f:
            links = json.load(f)

    url = None
    if name:
        url = links.get(name)
        if not url:
            return jsonify({"error": f"Unknown link name: {name}"}), 404

    if not url and raw_url:
        url = raw_url

    if not url:
        return jsonify({"error": "No valid URL or link name provided"}), 400

    if not url.startswith(("http://", "https://")):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    ok = open_url_locally(url)
    if ok:
        print(f"Opened link: {url}")
        return jsonify({"status": "ok", "opened": url}), 200
    else:
        return jsonify({"status": "error", "opened": url}), 500

# --- Run ----------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
