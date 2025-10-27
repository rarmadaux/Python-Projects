from flask import Flask, request, jsonify, render_template
import subprocess
import platform
import importlib
import os

# --- Detect OS ----------------------------------------------------
os_name = platform.system().lower()

print(f"Detected OS: {os_name}")

if os_name == "linux":
    audio_module = importlib.import_module("audio_linux")
elif os_name == "windows":
    audio_module = importlib.import_module("audio_windows")
else:
    raise SystemExit("❌ Unsupported OS — only Linux and Windows supported.")

# --- Flask App ----------------------------------------------------
app = Flask(__name__, template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/list_audio_apps")
def list_audio_apps():
    apps = audio_module.get_active_audio_apps()
    return jsonify(apps)

@app.route("/open_app", methods=["POST"])
def open_app():
    data = request.get_json()
    app_name = data.get("app")

    if not app_name:
        return jsonify({"error": "No app specified"}), 400

    try:
        if os_name == "windows":
            app_map = {
                "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                "thunderbird": r"C:\Program Files\Mozilla Thunderbird\thunderbird.exe",
                "discord": r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe",
                "explorer": "explorer.exe",
                "notepad": "notepad.exe",
                "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            }

            key = app_name.lower().split()[0]
            target = app_map.get(key, app_name)
            target = os.path.expandvars(target)

            print(f"→ Trying to open: {target}")

            if os.path.exists(target):
                os.startfile(target)
            else:
                subprocess.Popen(target, shell=True)

        else:
            subprocess.Popen(app_name.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"✅ Launched {app_name}")
        return jsonify({"status": "ok", "message": f"Opened {app_name}"}), 200

    except Exception as e:
        print(f"❌ Failed to open {app_name}: {e}")
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
