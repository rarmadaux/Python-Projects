import pulsectl

def set_app_volume(app_name, volume_level):
    pulse = pulsectl.Pulse("volume-control")
    volume_level = max(0.0, min(volume_level, 1.0))
    changed = False

    for sink_input in pulse.sink_input_list():
        name = sink_input.proplist.get("application.name", "").lower()
        if app_name.lower() in name:
            pulse.volume_set_all_chans(sink_input, volume_level)
            changed = True

    pulse.close()
    return changed


def get_active_audio_apps():
    pulse = pulsectl.Pulse("volume-reader")
    apps = []
    for sink_input in pulse.sink_input_list():
        name = sink_input.proplist.get("application.name", "Unknown")
        volume = round(sink_input.volume.value_flat, 2)
        apps.append({"name": name, "volume": volume})
    pulse.close()
    return apps

