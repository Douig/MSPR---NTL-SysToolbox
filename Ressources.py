import subprocess
#import json


def get_cpu_usage():
    try:
        command = [
            "powershell",
            "(Get-Counter '\\myasus\processeur(_total)\% temps processeur').CounterSamples.CookedValue"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        cpu = result.stdout.strip()
        #cpu = round(value, 2)

        print("CPU utilisé :",cpu,"%")
        return cpu

    except Exception as e:
        print("Erreur CPU :", e)
        return None

def get_ram_usage():
    try:
        command = [
            "powershell",
            "(Get-Counter '\\myasus\mémoire\pourcentage d’octets dédiés utilisés').CounterSamples.CookedValue"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        ram = round(float(result.stdout.strip()), 2)

        print("Ram utilisé:",ram,"%")
        return ram

    except Exception as e:
        print("Erreur RAM :", e)
        return None

def get_disk_usage():
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

        for disk_name, value in disks.items():
            print(disk_name,": ",value['usage_percent'],"% utilisé (Libre : ",value['free_GB'],"GB)")

        return disks

    except Exception as e:
        print("Erreur Disque :", e)
        return None


def get_resource_usage():
    
    print("\n--- Utilisation des ressources Windows ---")

    return {
        "cpu": get_cpu_usage(),
        "ram": get_ram_usage(),
        "disks": get_disk_usage()
    }
