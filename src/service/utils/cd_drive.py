import string
import ctypes


def get_cd_drive():

    drives = []

    bitmask = ctypes.windll.kernel32.GetLogicalDrives()

    for letter in string.ascii_uppercase:

        if bitmask & 1:
            drive = f"{letter}:\\"

            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)

            # DRIVE_CDROM = 5
            if drive_type == 5:
                drives.append(drive)

        bitmask >>= 1

    if drives:
        return drives[0]

    return None