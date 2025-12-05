import subprocess
import json
from datetime import datetime

def get_windows_version():
    try:
        command = [
            "powershell",
            "Get-ComputerInfo | Select-Object OsName, WindowsVersion, OsHardwareAbstractionLayer | ConvertTo-Json"
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        # Lire la sortie JSON
        data = json.loads(result.stdout)
        

        # Affichage CLI
        print("\n--- Version du système Windows ---")
        print("Système :",data.get("OsName"))
        print("Version :",data.get("WindowsVersion"))
        print("HAL     :",data.get("OsHardwareAbstractionLayer"))
        print("Date    :",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


        # Sauvegarde JSON
        #filename = f"diagnostic_windows_version_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        #with open(filename, "w") as f:
        #    json.dump(output, f, indent=4)

        #print("\nFichier JSON généré :" ,filename)

        return

    except Exception as e:
        print("Erreur lors de la récupération de la version Windows :", e)
        return None
