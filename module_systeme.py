# Fichier : module_systeme.py
import psutil
import platform
import time
import os

def monitor_linux():
    """
    Collecte et affichage métriques Linux (Ubuntu/Debian).
    """
    print("\n--- ANALYSE SYSTEME LINUX ---")
    
    # Identification OS (Parsing /etc/os-release)
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

    # Calcul Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    heures = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)

    # Collecte métriques Hardware
    # interval=1 : Bloquant pour calcul différentiel CPU
    cpu_usage = psutil.cpu_percent(interval=1)
    
    ram = psutil.virtual_memory()
    ram_total = round(ram.total / (1024**3), 2)
    ram_used = round(ram.used / (1024**3), 2)
    ram_percent = ram.percent

    disk = psutil.disk_usage('/')
    disk_total = round(disk.total / (1024**3), 2)
    disk_used = round(disk.used / (1024**3), 2)
    disk_percent = disk.percent

    # Affichage stdout
    print("-" * 40)
    print(f"OS       : {os_name} (Kernel {os_release})")
    print(f"Uptime   : {heures}h {minutes}m")
    print("-" * 40)
    print(f"CPU      : {cpu_usage}%")
    print(f"RAM      : {ram_used}Go / {ram_total}Go ({ram_percent}%)")
    print(f"Disque / : {disk_used}Go / {disk_total}Go ({disk_percent}%)")
    print("-" * 40)
    
    input("\nEntrée pour continuer...")

def monitor_windows():
    """
    Stub pour future implémentation Windows (WMI/PowerShell).
    """
    print("\n--- ANALYSE SYSTEME WINDOWS ---")
    print("Fonctionnalité non implémentée.")
    print("TODO: Intégrer logique WMI.")
    print("-" * 40)
    
    input("\nEntrée pour continuer...")