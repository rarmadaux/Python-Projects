from flask import Flask, request, jsonify
import subprocess
import pulsectl

app = Flask(__name__)

# --- Helpers ------------------------------------------------------

def set_app_volume(app_name, volume_level):
    """
    Set the volume (0.0 - 1.0) for a given application name (case-insensitive)
    using PulseAudio / PipeWire.
    """
    pulse = pulsectl.Pulse('volume-control')
    volume_level = max(0.0, min(volume_level, 1.0))  # Clamp between 0 and 1
    changed = False

    for sink_input in pulse.sink_input_list():
        name = sink_input.proplist.get('application.name', '').lower()
        if app_name.lower() in name:
            pulse.volume_set_all_chans(sink_input, volume_level)
            changed = True

    pulse.close()
    return changed


def get_active_audio_apps():
    """Return list of apps with active audio streams and their current volume."""
    pulse = pulsectl.Pulse('volume-reader')
    apps = []
    for sink_input in pulse.sink_input_list():
        name = sink_input.proplist.get('application.name', 'Unknown')
        volume = round(sink_input.volume.value_flat, 2)
        apps.append({"name": name, "volume": volume})
    pulse.close()
    return apps


# --- Routes -------------------------------------------------------

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>PC Controller</title>
        <style>
            body {
                margin: 0;
                font-family: sans-serif;
                background: #0e1117;
                color: #fff;
                display: flex;
                height: 100vh;
                overflow: hidden;
            }
            /* Sidebar with app icons */
            #sidebar {
                background: #1a1f29;
                width: 90px;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 10px 5px;
                box-shadow: 2px 0 10px rgba(0,0,0,0.4);
                overflow-y: auto;
            }
            .app-icon {
                width: 64px;
                height: 64px;
                border-radius: 16px;
                background: #2b3244;
                display: flex;
                justify-content: center;
                align-items: center;
                cursor: pointer;
                margin: 10px 0;
                transition: transform 0.15s, background 0.2s;
            }
            .app-icon:hover {
                transform: scale(1.1);
                background: #5865F2;
            }
            .app-icon img {
                width: 42px;
                height: 42px;
            }
            button.refresh {
                background: #5865F2;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-size: 14px;
                cursor: pointer;
                margin-top: 10px;
                box-shadow: 0 4px 10px rgba(88,101,242,0.3);
            }
            /* Main panel with volume sliders */
            #main {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                overflow-y: auto;
                padding: 10px;
            }
            #apps {
                display: flex;
                justify-content: flex-start;
                align-items: flex-end;
                flex-wrap: wrap;
                gap: 20px;
            }
            .app {
                background: #1a1f29;
                border-radius: 12px;
                padding: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                width: 80px;
                display: flex;
                flex-direction: column;
                align-items: center;
                position: relative;
            }
            .app-name {
                font-size: 13px;
                text-align: center;
                margin-bottom: 5px;
            }
            input[type=range][orient=vertical] {
                writing-mode: bt-lr; /* IE */
                -webkit-appearance: slider-vertical; /* Chrome/Safari */
                width: 10px;
                height: 120px;
                accent-color: #5865F2;
                margin: 10px 0;
            }
            .hide-btn {
                background: none;
                border: none;
                color: #aaa;
                font-size: 18px;
                cursor: pointer;
                position: absolute;
                top: 5px;
                right: 5px;
                transition: color 0.2s;
            }
            .hide-btn:hover {
                color: #fff;
            }
        </style>
    </head>
    <body>
        <div id="sidebar">
            <div class="app-icon" title="Thunderbird" onclick="openApp('thunderbird')">
                <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/thunderbird.svg" alt="Thunderbird">
            </div>
            <div class="app-icon" title="Discord" onclick="openApp('flatpak run com.discordapp.Discord')">
                <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/discord.svg" alt="Discord">
            </div>
            <div class="app-icon" title="Firefox" onclick="openApp('firefox')">
                <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/firefox.svg" alt="Firefox">
            </div>
            <button class="refresh" onclick="loadApps()">🔄</button>
        </div>

        <div id="main">
            <h2>🔊 Volume</h2>
            <div id="apps"></div>
        </div>

        <script>
            const hiddenApps = new Set();

            async function loadApps() {
                const container = document.getElementById('apps');
                container.innerHTML = "<p>Loading...</p>";
                const res = await fetch('/list_audio_apps');
                const apps = await res.json();
                container.innerHTML = '';

                // Deduplicate by lowercase name
                const unique = [];
                const seen = new Set();
                for (const app of apps) {
                    const key = app.name.toLowerCase();
                    if (!seen.has(key)) {
                        seen.add(key);
                        unique.push(app);
                    }
                }

                unique.forEach(app => {
                    if (hiddenApps.has(app.name)) return;
                    const div = document.createElement('div');
                    div.className = 'app';
                    div.innerHTML = `
                        <button class="hide-btn" title="Hide" onclick="toggleVisibility('${app.name}')">👁️</button>
                        <div class="app-name">${app.name}</div>
                        <input type="range" orient="vertical" min="0" max="1" step="0.01" value="${app.volume}" 
                            oninput="updateVolume('${app.name}', this.value)">
                        <div>${Math.round(app.volume * 100)}%</div>
                    `;
                    container.appendChild(div);
                });
            }

            async function updateVolume(appName, value) {
                await fetch('/set_volume', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ app: appName, volume: parseFloat(value) })
                });
            }

            async function openApp(appName) {
                await fetch('/open_app', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ app: appName })
                });
            }

            function toggleVisibility(appName) {
                if (hiddenApps.has(appName)) hiddenApps.delete(appName);
                else hiddenApps.add(appName);
                loadApps();
            }

            loadApps();
        </script>
    </body>
    </html>
    """



@app.route('/list_audio_apps')
def list_audio_apps():
    """Return list of active audio apps."""
    apps = get_active_audio_apps()
    return jsonify(apps)


@app.route('/open_app', methods=['POST'])
def open_app():
    data = request.get_json()
    app_name = data.get('app')

    if not app_name:
        return jsonify({"error": "No app specified"}), 400

    try:
        subprocess.Popen([app_name])
        return jsonify({"status": "ok", "message": f"Opened {app_name}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/set_volume', methods=['POST'])
def set_volume():
    data = request.get_json()
    app_name = data.get('app')
    volume = data.get('volume')

    if app_name is None or volume is None:
        return jsonify({"error": "app and volume required"}), 400

    success = set_app_volume(app_name, float(volume))

    if success:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({"status": "not_found"}), 404


if __name__ == '__main__':
    # 0.0.0.0 → allows phone to connect via LAN
    app.run(host='0.0.0.0', port=5000)
