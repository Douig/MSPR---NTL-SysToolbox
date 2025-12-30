import subprocess
import json
from datetime import datetime


def get_windows_uptime(print_output=True):
    try:
        
        command = [
            "powershell",
            "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime | get-Date -format 'yyyy-MM-dd HH:mm:ss' "
        ]

        # Exécution de la commande
        result = subprocess.run(command, capture_output=True, text=True)
        boot_str = result.stdout.strip()         #strip() enleve les especes inutiles

        # Transforme la date en texte en objet date Python
        boot_time = datetime.strptime(boot_str, "%Y-%m-%d %H:%M:%S")   # text->date P comme Parser (analyser un texte)

        # Maintenant (heure locale)
        now = datetime.now()

        # Calcul uptime
        uptime = now - boot_time

        # Format lisible
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60

        
        print("\n--- Uptime du système Windows ---")
        print("Dernier démarrage :",boot_time.strftime('%Y-%m-%d %H:%M:%S'))  #date ->texte F comme Format pour afficher
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


def get_windows_version(print_output=True):
    try:
        command = [
            "powershell",
            "Get-ComputerInfo | Select-Object OsName, WindowsVersion, OsHardwareAbstractionLayer | ConvertTo-Json"
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        # Lire la sortie JSON EN DICTIONNAIRE 
        data = json.loads(result.stdout)
        

        # Affichage CLI
        if print_output:
            print("\n--- Version du système Windows ---")
            print("Système :",data.get("OsName"))
            print("Version :",data.get("WindowsVersion"))
            print("HAL     :",data.get("OsHardwareAbstractionLayer"))
            print("Date    :",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return {
            "os_name": data.get("OsName"),
            "windows_version": data.get("WindowsVersion"),
            "hal": data.get("OsHardwareAbstractionLayer"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        print("Erreur lors de la récupération de la version Windows :", e)
        return None


def get_cpu_usage(print_output=True):
    try:
        command = [
            "powershell",
            "(Get-Counter '\\\\myasus\\processeur(_total)\\% temps processeur').CounterSamples.CookedValue"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        cpu_str = result.stdout.strip().replace(",", ".") 
        cpu = round(float(cpu_str), 2)

        if print_output:
            print("CPU utilisé :", cpu, "%")
        return cpu

    except Exception as e:
        print("Erreur CPU :", e)
        return None


def get_ram_usage(print_output=True):
    try:
        command = [
            "powershell",
            '(Get-Counter "\\Mémoire\\Pourcentage d’octets dédiés utilisés").CounterSamples.CookedValue'
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        ram_str = result.stdout.strip().replace(",", ".")
        ram = round(float(ram_str), 2)
        

        if print_output:
            print("RAM utilisée :", ram, "%")
        return ram

    except Exception as e:
        print("Erreur RAM :", e)
        return None


def get_disk_usage(print_output=True):
    try:
        command = [
            "powershell",
            "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout.strip()

        disks = {}

        
        lines = output.splitlines()[2:]  # on saute les deux premières lignes
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                name = parts[0]
                used = int(parts[1])
                free = int(parts[2])
                total = used + free
                percent_used = round((used / total) * 100, 2)


                #Je convertie l'octet en gb binaire (GiB (Gio) binaire = division par 1024³)
                
                disks[name] = {
                    "used_GB": round(used / (1024**3), 2),
                    "free_GB": round(free / (1024**3), 2),
                    "usage_percent": percent_used
                }

        if print_output:
            for disk_name, value in disks.items():
                print(disk_name,": ",value['usage_percent'],"% utilisé (Libre : ",value['free_GB'],"GB)")

        return disks

    except Exception as e:
        print("Erreur Disque :", e)
        return None


def get_resource_usage(print_output=True):
    
    if print_output:
        print("\n--- Utilisation des ressources Windows ---")

    return {
        "cpu": get_cpu_usage(print_output=print_output),
        "ram": get_ram_usage(print_output=print_output),
        "disks": get_disk_usage(print_output=print_output)
    }


def generate_diagnostic_json():
    """Génère un fichier JSON détaillé avec tous les diagnostics"""
    try:
        diagnostic_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": get_windows_version(print_output=False),
            "uptime": get_windows_uptime(print_output=False),
            "resources": {
                "cpu_percent": get_cpu_usage(print_output=False),
                "ram_percent": get_ram_usage(print_output=False),
                "disks": get_disk_usage(print_output=False)
            }
        }
        
        # Créer le nom du fichier avec timestamp
        filename = f"diagnostic_windows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Sauvegarder en JSON
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(diagnostic_data, f, indent=4, ensure_ascii=False)
        
        print(f"\n Fichier JSON généré : {filename}")
        return filename
    
    except Exception as e:
        print(f"Erreur lors de la génération du JSON : {e}")
        return None
