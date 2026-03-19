import winreg
import os
from src.service.utils.epic_games import get_epic_games


def get_installed_programs():

    epic_games = get_epic_games()
    epic_games = get_epic_games()
    for game in epic_games:
        if "icon" not in game:
            game["icon"] = game["exe"]
            
    programs = [] + epic_games

    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for root, path in registry_paths:

        try:
            key = winreg.OpenKey(root, path)

            for i in range(winreg.QueryInfoKey(key)[0]):

                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)

                    name = None
                    install_location = None
                    display_icon = None
                    uninstall_string = None

                    try:
                        name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    except:
                        pass

                    try:
                        install_location, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                    except:
                        pass

                    try:
                        display_icon, _ = winreg.QueryValueEx(subkey, "DisplayIcon")
                    except:
                        pass

                    try:
                        uninstall_string, _ = winreg.QueryValueEx(subkey, "UninstallString")
                    except:
                        pass

                    if not name:
                        continue

                    exe_path = None
                    icon_path = None

                    # =====================
                    # procurar exe na pasta
                    # =====================

                    if install_location and os.path.exists(install_location):

                        for file in os.listdir(install_location):

                            if file.lower().endswith(".exe"):

                                exe_path = os.path.join(install_location, file)
                                break

                    # =====================
                    # tentar DisplayIcon
                    # =====================

                    if display_icon:

                        icon_candidate = display_icon.split(",")[0]

                        if os.path.exists(icon_candidate):
                            icon_path = icon_candidate

                        if not exe_path and icon_candidate.lower().endswith(".exe"):
                            exe_path = icon_candidate

                    # =====================
                    # tentar UninstallString
                    # =====================

                    if not exe_path and uninstall_string:

                        uninstall_clean = uninstall_string.replace('"', '').split(" ")[0]

                        if uninstall_clean.lower().endswith(".exe") and os.path.exists(uninstall_clean):

                            exe_path = uninstall_clean

                    # fallback de icone
                    if not icon_path and exe_path:
                        icon_path = exe_path

                    # ignorar programas sem executável
                    if not exe_path:
                        continue

                    programs.append({
                        "name": name,
                        "exe": exe_path,
                        "icon": icon_path
                    })

                except:
                    pass

        except:
            pass

    # remover duplicados
    seen = set()
    unique_programs = []

    for program in programs:

        identifier = program["exe"]

        if identifier not in seen:

            seen.add(identifier)
            unique_programs.append(program)

    unique_programs.sort(key=lambda x: x["name"].lower())
    return unique_programs