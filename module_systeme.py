import psutil
import platform
import time
import os
import subprocess
import json
import datetime 

# ==========================================
# PARTIE 1 : LINUX
# ==========================================
def monitor_linux():
    print("\n--- ANALYSE SYSTEME LINUX ---")
    print("(Patientez 1s pour le calcul CPU...)")
    
    # 1. INFO OS
    os_name = platform.system()
    os_release = platform.release()
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME"):
                    os_name = line.split("=")[1].strip().strip('"')
                    break
    except:
        pass 

    # 2. UPTIME
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    heures = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)

    # 3. METRIQUES
    cpu_usage = psutil.cpu_percent(interval=1)
    
    ram = psutil.virtual_memory()
    ram_total = round(ram.total / (1024**3), 2)
    ram_used = round(ram.used / (1024**3), 2)
    
    disk = psutil.disk_usage('/')
    disk_total = round(disk.total / (1024**3), 2)
    disk_used = round(disk.used / (1024**3), 2)

    # --- CONSTRUCTION DU DICTIONNAIRE DE DONNÉES ---
    # CORRECTION ICI : datetime.datetime.now()
    data_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "os_info": {
            "name": os_name,
            "kernel": os_release
        },
        "uptime": {
            "heures": heures,
            "minutes": minutes
        },
        "metrics": {
            "cpu_percent": cpu_usage,
            "ram": {"used_go": ram_used, "total_go": ram_total, "percent": ram.percent},
            "disk_root": {"used_go": disk_used, "total_go": disk_total, "percent": disk.percent}
        }
    }

    # --- AFFICHAGE CLASSIQUE ---
    print("-" * 40)
    print(f"OS       : {os_name} (Kernel {os_release})")
    print(f"Uptime   : {heures}h {minutes}m")
    print("-" * 40)
    print(f"CPU      : {cpu_usage}%")
    print(f"RAM      : {ram_used}Go / {ram_total}Go ({ram.percent}%)")
    print(f"Disque / : {disk_used}Go / {disk_total}Go ({disk.percent}%)")
    print("-" * 40)
    
    # --- GESTION JSON ---
    choix_json = input("\nExporter ce rapport en JSON ? (o/n) : ")
    
    if choix_json.lower() == 'o':
        # Affichage Console
        json_str = json.dumps(data_report, indent=4)
        print("\n--- APERÇU JSON ---")
        print(json_str)
        
        # Sauvegarde Fichier
        save = input("Sauvegarder dans un fichier ? (o/n) : ")
        if save.lower() == 'o':
            folder = "rapports_json"
            os.makedirs(folder, exist_ok=True)
            
            # CORRECTION ICI : datetime.datetime.now() (C'était déjà bon, mais on confirme)
            filename = f"{folder}/report_linux_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(filename, "w") as f:
                    f.write(json_str)
                print(f"[OK] Fichier créé : {filename}")
            except Exception as e:
                print(f"[ERREUR] Écriture impossible : {e}")

    input("\nAppuyez sur Entrée pour revenir...")

# ==========================================
# PARTIE 2 : WINDOWS (PowerShell)
# ==========================================

def get_windows_version():
    try:
        cmd = ["powershell", "Get-ComputerInfo | Select-Object OsName, WindowsVersion | ConvertTo-Json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        return {"name": data.get('OsName'), "version": data.get('WindowsVersion')}
    except Exception:
        return {"name": "Inconnu", "version": "Inconnu"}

def get_windows_uptime():
    try:
        cmd = ["powershell", "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime | get-Date -format 'yyyy-MM-dd HH:mm:ss'"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        boot_str = result.stdout.strip()
        
        boot_time = datetime.datetime.strptime(boot_str, "%Y-%m-%d %H:%M:%S")
        uptime = datetime.datetime.now() - boot_time
        
        # On retourne un dictionnaire avec les infos brutes et formatées
        return {
            "last_boot": boot_str,
            "days": uptime.days,
            "hours": uptime.seconds // 3600,
            "minutes": (uptime.seconds % 3600) // 60
        }
    except Exception:
        return None

def get_cpu_usage():
    try:
        # Attention : "processeur" fonctionne sur Windows FR. Sur EN mettre "Processor"
        cmd = ["powershell", "(Get-Counter '\\processeur(_total)\\% temps processeur').CounterSamples.CookedValue"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        val = round(float(result.stdout.strip().replace(",", ".")), 2)
        return val
    except Exception:
        return 0.0

def get_ram_usage():
    try:
        cmd = ["powershell", '(Get-Counter "\\Mémoire\\Pourcentage d’octets dédiés utilisés").CounterSamples.CookedValue']
        result = subprocess.run(cmd, capture_output=True, text=True)
        val = round(float(result.stdout.strip().replace(",", ".")), 2)
        return val
    except Exception:
        return 0.0

def get_disk_usage():
    disks_list = []
    try:
        cmd = ["powershell", "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()[2:]
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                name = parts[0]
                used = int(parts[1])
                free = int(parts[2])
                total = used + free
                percent = round((used / total) * 100, 2)
                
                # Conversion en Go pour le JSON
                used_go = round(used / (1024**3), 2)
                total_go = round(total / (1024**3), 2)
                
                disks_list.append({
                    "mount_point": name,
                    "used_go": used_go,
                    "total_go": total_go,
                    "percent": percent
                })
    except Exception:
        pass
    return disks_list

def get_service_status():
    try:
        cmd1 = ["powershell", "-Command", "(Get-Service -Name 'DNS' -ErrorAction SilentlyContinue).Status"]
        cmd2 = ["powershell", "-Command", "(Get-Service -Name 'NTDS' -ErrorAction SilentlyContinue).Status"]
        
        r1 = subprocess.run(cmd1, capture_output=True, text=True)
        r2 = subprocess.run(cmd2, capture_output=True, text=True)
        
        dns = r1.stdout.strip() if r1.stdout.strip() else "Non installé"
        ntds = r2.stdout.strip() if r2.stdout.strip() else "Non installé"
        return {"DNS": dns, "ActiveDirectory_NTDS": ntds}
    except:
        return {"DNS": "Erreur", "ActiveDirectory_NTDS": "Erreur"}

def monitor_windows():
    """Fonction principale Windows avec Export JSON"""
    print("\n--- ANALYSE SYSTEME WINDOWS (PowerShell) ---")
    print("(Patientez quelques secondes...)")
    
    # 1. Collecte des données via les fonctions modifiées
    os_info = get_windows_version()
    uptime_info = get_windows_uptime()
    cpu = get_cpu_usage()
    ram = get_ram_usage()
    disks = get_disk_usage()
    services = get_service_status()

    # 2. Construction du Dictionnaire global pour le JSON
    data_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "os_info": os_info,
        "uptime": uptime_info,
        "metrics": {
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disks": disks
        },
        "services": services
    }

    # 3. Affichage Console (basé sur les données collectées)
    print("-" * 30)
    print(f"Système : {os_info['name']}")
    print(f"Version : {os_info['version']}")
    
    print("-" * 30)
    if uptime_info:
        print(f"Dernier démarrage : {uptime_info['last_boot']}")
        print(f"Uptime : {uptime_info['days']}j {uptime_info['hours']}h {uptime_info['minutes']}m")
    else:
        print("Erreur Uptime")

    print("-" * 30)
    print(f"CPU utilisé : {cpu} %")
    print(f"RAM utilisée : {ram} %")

    print("-" * 30)
    if disks:
        for d in disks:
            print(f"Disque {d['mount_point']} : {d['percent']}% utilisé ({d['used_go']}Go / {d['total_go']}Go)")
    else:
        print("Aucun disque détecté ou erreur.")

    print("-" * 30)
    print(f"Service DNS  : {services['DNS']}")
    print(f"Service NTDS : {services['ActiveDirectory_NTDS']} (Active Directory)")

    # 4. Gestion JSON (Interactif)
    choix_json = input("\nExporter ce rapport en JSON ? (o/n) : ")
    
    if choix_json.lower() == 'o':
        json_str = json.dumps(data_report, indent=4)
        print("\n--- APERÇU JSON ---")
        print(json_str)
        
        save = input("Sauvegarder dans un fichier ? (o/n) : ")
        if save.lower() == 'o':
            folder = "rapports_json"
            os.makedirs(folder, exist_ok=True)
            
            filename = f"{folder}/report_windows_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(filename, "w", encoding='utf-8') as f:
                    f.write(json_str)
                print(f"[OK] Fichier créé : {filename}")
            except Exception as e:
                print(f"[ERREUR] Écriture impossible : {e}")

    input("\nAppuyez sur Entrée pour revenir...")