import os
import shutil
import winshell
from win32com.client import Dispatch

APP_DIR = r"C:\Program Files\CD Launcher"
STARTUP = winshell.startup()

os.makedirs(APP_DIR, exist_ok=True)

# copiar executáveis
shutil.copy("CDLauncherGUI.exe", APP_DIR)
shutil.copy("CDLauncherWatcher.exe", APP_DIR)

# criar atalho desktop
desktop = winshell.desktop()
path = os.path.join(desktop, "CD Launcher.lnk")
target = os.path.join(APP_DIR, "CDLauncherGUI.exe")

shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(path)
shortcut.Targetpath = target
shortcut.WorkingDirectory = APP_DIR
shortcut.save()

# criar watcher startup
startup_vbs = os.path.join(STARTUP, "CDLauncherWatcher.vbs")
with open(startup_vbs, "w") as f:
    f.write(f'''
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{APP_DIR}\\CDLauncherWatcher.exe""", 0
Set WshShell = Nothing
''')

print("Instalado com sucesso")