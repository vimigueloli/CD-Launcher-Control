import os
import json

def get_epic_games():

    manifest_path = r"C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"

    games = []

    if not os.path.exists(manifest_path):
        return games

    for file in os.listdir(manifest_path):

        if file.endswith(".item"):

            full_path = os.path.join(manifest_path, file)

            try:
                with open(full_path, encoding="utf-8") as f:
                    data = json.load(f)

                name = data.get("DisplayName")
                install = data.get("InstallLocation")
                exe = data.get("LaunchExecutable")

                exe_path = None

                if install and exe:
                    exe_path = os.path.join(install, exe)

                games.append({
                    "name": name,
                    "exe": exe_path
                })

            except:
                pass

    return games