import comtypes
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

def ensure_com_initialized():
    """Ensure COM library is initialized in the current thread."""
    try:
        comtypes.CoInitialize()
    except Exception:
        pass  # Already initialized

def set_app_volume(app_name, volume_level):
    ensure_com_initialized()
    volume_level = max(0.0, min(volume_level, 1.0))
    changed = False

    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        process = session.Process
        if process and app_name.lower() in process.name().lower():
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume.SetMasterVolume(volume_level, None)
            changed = True

    return changed

def get_active_audio_apps():
    ensure_com_initialized()
    apps = []
    sessions = AudioUtilities.GetAllSessions()

    for session in sessions:
        process = session.Process
        if not process:
            continue
        try:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume).GetMasterVolume()
            apps.append({"name": process.name(), "volume": round(volume, 2)})
        except Exception:
            continue

    return apps
