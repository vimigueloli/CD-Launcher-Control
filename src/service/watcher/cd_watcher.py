import os
import json
import time
import subprocess
import ctypes

CONFIG_DIR = os.path.join(os.getenv("APPDATA"), "CDLauncher")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

last_executed = None


def is_service_active():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("active", False)
    except:
        return False

def apply_display_mode(mode):
    import subprocess
    import time

    mapping = {
        "primary": "/internal",
        "second_screen": "/external",
        "extend": "/extend",
        "duplicate": "/clone"
    }

    if mode in mapping:
        subprocess.Popen([
            "C:\\Windows\\System32\\DisplaySwitch.exe",
            mapping[mode]
        ])
        time.sleep(2)  # espera mudança de tela aplicar

def focus_window_by_pid(pid, timeout=10):
    import time
    import win32gui
    import win32process
    import win32con
    import win32com.client

    shell = win32com.client.Dispatch("WScript.Shell")
    start = time.time()

    while time.time() - start < timeout:
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    try:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        shell.SendKeys('%')  # hack necessário pro Windows permitir foco
                        win32gui.SetForegroundWindow(hwnd)
                    except:
                        pass
                    return False
            return True

        win32gui.EnumWindows(callback, None)
        time.sleep(0.3)

def get_cd_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()

    for letter in range(26):
        if bitmask & (1 << letter):
            drive = f"{chr(65 + letter)}:\\"
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)

            # 5 = CDROM
            if drive_type == 5:
                drives.append(drive)

    return drives

def wait_for_steam(timeout=15):
    import psutil
    import time

    start = time.time()

    while time.time() - start < timeout:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and "steam" in proc.info['name'].lower():
                time.sleep(3)  # dá tempo do big picture abrir
                return
        time.sleep(0.5)

def close_cd_explorer():
    import win32gui
    import win32process

    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if title and ("CD" in title or "DVD" in title):
            win32gui.PostMessage(hwnd, 0x0010, 0, 0)  # WM_CLOSE
        return True

    win32gui.EnumWindows(callback, None)

def launch_steam_big_picture():
    import subprocess
    import time
    import psutil
    import os

    steam_running = False

    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and "steam.exe" in proc.info['name'].lower():
            steam_running = True
            break

    if steam_running:
        # 🔥 força Big Picture na steam já aberta
        os.startfile("steam://open/bigpicture")
    else:
        # 🔥 inicia já em Big Picture
        subprocess.Popen([
            r"C:\Program Files (x86)\Steam\Steam.exe",
            "-bigpicture"
        ])

    # pequena espera pra interface aparecer
    time.sleep(4)

def execute_json(json_path):
    global last_executed

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data["action"] == "launch_program":

            apply_display_mode(data.get("display_mode", "primary"))
            if data.get("big_picture"):
                launch_steam_big_picture()

            proc = subprocess.Popen(data["exe"])

            # 🔥 forçar foco no jogo
            focus_window_by_pid(proc.pid)

        elif data["action"] == "open_web":
            import webbrowser
            webbrowser.open(data["url"])

    except Exception as e:
        print("Erro executando JSON:", e)


def watch_cd():
    global last_executed

    while True:
        if not is_service_active():
            time.sleep(2)
            continue

        drives = get_cd_drives()

        found = False

        for drive in drives:
            json_path = os.path.join(drive, "launch.json")

            if os.path.exists(json_path):
                close_cd_explorer()  # fecha o explorer do CD para evitar bloqueio do arquivo
                found = True

                if json_path != last_executed:
                    print("Executando:", json_path)
                    execute_json(json_path)
                    last_executed = json_path

        # se nenhum CD encontrado, reset
        if not found:
            last_executed = None

        time.sleep(2)