import subprocess
import os
from src.service.utils.cd_drive import get_cd_drive


def write_json_to_cd(json_path, progress_callback=None):

    drive = get_cd_drive()

    if not drive:
        return False, "Nenhum leitor de CD encontrado"

    json_path = os.path.abspath(json_path)

    ps_script = f"""
$recorder = New-Object -ComObject IMAPI2.MsftDiscRecorder2 
$master = New-Object -ComObject IMAPI2.MsftDiscMaster2
$recorder.InitializeDiscRecorder($master.Item(0))
$writer = New-Object -ComObject IMAPI2.MsftDiscFormat2Data
$writer.Recorder = $recorder 
$writer.ClientName = "CDLauncher" 
$image = New-Object -ComObject IMAPI2FS.MsftFileSystemImage 
$image.ChooseImageDefaults($recorder) 
# --- NOVIDADE: IMPORTAR SESSÃO EXISTENTE --- 
if ($writer.MediaHeuristicallyBlank -eq $false) {{
    $image.MultisessionInterfaces = $writer.MultisessionInterfaces
    $image.ImportFileSystem() | Out-Null
}}
# Definir sistemas de arquivos (UDF/Joliet/ISO) 
$image.FileSystemsToCreate = 7 # Recomendado usar 7 para maior compatibilidade 
# --- NOVIDADE: SOBRESCREVER ARQUIVO --- 
# Se o arquivo já existir no índice, removemos a referência antiga antes de adicionar a nova 
if ($image.Root.Exists("launch.json")) {{
    $image.Root.RemoveTree("launch.json") 
}} # Carregar o novo JSON 
$stream = New-Object -ComObject ADODB.Stream 
$stream.Type = 1 
$stream.Open() 
$stream.LoadFromFile("{json_path}") 
$image.Root.AddFile("launch.json", $stream) 
# Criar a imagem de resultado 
$result = $image.CreateResultImage() 
# --- NOVIDADE: MANTER DISCO ABERTO --- 
$writer.CloseMedia = $false # Permite que você grave mais vezes depois 
Write-Host "Gravando nova sessão..." 
$writer.Write($result.ImageStream) 
Write-Host "Gravação concluída"
Start-Sleep -Seconds 2
$recorder.EjectMedia()
"""

    try:

        process = subprocess.Popen(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # importante!
            text=True,
            bufsize=1
        )

        output = ""

        # 🔥 leitura NÃO BLOQUEANTE em tempo real
        for line in iter(process.stdout.readline, ''):
            line = line.strip()

            if line:
                print(line)
                output += line + "\n"

                if progress_callback:
                    progress_callback(line)

        # 🔥 ESSENCIAL
        process.communicate()

        if process.returncode == 0:
            return True, output
        else:
            return False, output

    except Exception as e:

        return False, str(e)