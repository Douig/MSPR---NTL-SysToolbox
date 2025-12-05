import subprocess
from datetime import datetime

def gggget_windows_version():
    try:
        command = [
            "powershell",
            "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsHardwareAbstractionLayer"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout.strip()

        data = {}

        lines = output.splitlines()
        
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()

        print("\n--- Version du système Windows ---")
        print("Système :", data.get("WindowsProductName"))
        print("Version :", data.get("WindowsVersion"))
        print("HAL     :", data.get("OsHardwareAbstractionLayer"))
        #print("Date    :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return data

    except Exception as e:
        print("Erreur :", e)
        return None

