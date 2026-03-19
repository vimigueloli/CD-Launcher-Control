import subprocess
import os
from src.service.utils.cd_drive import get_cd_drive


def write_json_to_cd(json_path):

    drive = get_cd_drive()

    if not drive:
        return False, "Nenhum leitor de CD encontrado"

    json_path = os.path.abspath(json_path)

    ps_script = f"""
$recorder = New-Object -ComObject IMAPI2.MsftDiscRecorder2
$master = New-Object -ComObject IMAPI2.MsftDiscMaster2
$recorder.InitializeDiscRecorder($master.Item(0))

# detectar mídia
$writer = New-Object -ComObject IMAPI2.MsftDiscFormat2Data
$writer.Recorder = $recorder
$writer.ClientName = "CDLauncher"

# tentar apagar disco se não estiver vazio
if ($writer.MediaHeuristicallyBlank -eq $false) {{

    Write-Host "Tentando apagar disco..."

    try {{

        $eraser = New-Object -ComObject IMAPI2.MsftDiscFormat2Erase
        $eraser.Recorder = $recorder
        $eraser.ClientName = "CDLauncher"
        $eraser.FullErase = $true

        $eraser.EraseMedia()

        Write-Host "Disco apagado"

    }} catch {{

        Write-Host "Não foi possível apagar disco (talvez seja CD-R)"

    }}
}}

Write-Host "Criando nova imagem..."

$image = New-Object -ComObject IMAPI2FS.MsftFileSystemImage
$image.ChooseImageDefaults($recorder)
$image.FileSystemsToCreate = 4
$image.VolumeName = "CDLAUNCHER"

$stream = New-Object -ComObject ADODB.Stream
$stream.Type = 1
$stream.Open()
$stream.LoadFromFile("{json_path}")

$image.Root.AddFile("launch.json", $stream)

$result = $image.CreateResultImage()

Write-Host "Gravando disco..."

$writer.Write($result.ImageStream)

Write-Host "Gravação concluída"
"""

    try:

        process = subprocess.Popen(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output = ""

        for line in process.stdout:
            print(line.strip())
            output += line

        process.wait()

        if process.returncode == 0:
            return True, output
        else:
            return False, output

    except Exception as e:

        return False, str(e)