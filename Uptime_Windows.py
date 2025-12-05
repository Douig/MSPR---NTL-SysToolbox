import subprocess
from datetime import datetime

def get_windows_uptime():
    try:
        # Commande PowerShell
        command = [
            "powershell",
            "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime | get-Date -format 'yyyy-MM-dd HH:mm:ss' "
        ]

        # Exécution de la commande
        result = subprocess.run(command, capture_output=True, text=True)
        boot_str = result.stdout.strip()

        # Convertir la date PowerShell
        boot_time = datetime.strptime(boot_str, "%Y-%m-%d %H:%M:%S")

        # Maintenant (heure locale)
        now = datetime.now()

        # Calcul uptime
        uptime = now - boot_time

        # Format lisible
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60

        print("\n--- Uptime du système Windows ---")
        print("Dernier démarrage :",boot_time.strftime('%Y-%m-%d %H:%M:%S'))
        print("Uptime :",days,"jours,", hours, "heures,", minutes," minutes")

        return {
            "last_boot": boot_time.strftime('%Y-%m-%d %H:%M:%S'),
            "uptime_days": days,
            "uptime_hours": hours,
            "uptime_minutes": minutes
        }

    except Exception as e:
        print("Erreur lors de la récupération de l'uptime :", e)
        return None
