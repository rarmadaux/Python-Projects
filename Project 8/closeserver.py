import psutil
import os

def stop_flask():
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = " ".join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ""
            if "flask" in cmdline or "app.py" in cmdline:
                print(f"Killing Flask server (PID: {proc.info['pid']})")
                proc.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed == 0:
        print("No running Flask server found.")
    else:
        print(f"✅ Stopped {killed} Flask server(s).")

if __name__ == "__main__":
    stop_flask()

