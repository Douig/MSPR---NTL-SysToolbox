# Fichier : module_audit.py
import sys
import platform
import csv
import json
import os
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
Fichier_EOL = "eol_reference.csv"
Fichier_Rapport_Final = "rapport_audit" 

def OS_Info():
    """Identifie l'OS et la version précise pour comparaison"""
    os_name = "Windows" if sys.platform == "win32" else "Linux"
    version = platform.release()
    
    if os_name == "Linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        # Ex: "Ubuntu 22.04.1 LTS"
                        version = line.split("=")[1].strip().strip('"')
        except:
            pass
    
    # Retourne une chaîne complète pour faciliter la recherche (ex: "Windows 10" ou "Ubuntu 20.04")
    return f"{os_name} {version}"

def scanner_applications_locales():
    """Scanne le système pour lister toutes les applications installées"""
    apps = []
    nom_machine = platform.node()
    
    if sys.platform == "win32":
        import winreg
        paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        for path in paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        sub_key_name = winreg.EnumKey(key, i)
                        sub_key = winreg.OpenKey(key, sub_key_name)
                        name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                        try:
                            version = winreg.QueryValueEx(sub_key, "DisplayVersion")[0]
                        except:
                            version = ""
                        apps.append({"nom_machine": nom_machine, "version": f"{name} {version}"})
                    except: continue
            except: continue
    else:
        # Scan Linux (dpkg)
        try:
            result = subprocess.check_output(["dpkg-query", "-W", "-f=${Package} ${Version}\n"], text=True)
            for line in result.strip().split('\n'):
                apps.append({"nom_machine": nom_machine, "version": line})
        except: pass
    return apps

def verifier_date(ref_date):
    """Calcule le statut et le niveau d'alerte en fonction de la date"""
    try:
        eol_dt = datetime.strptime(ref_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        diff = (eol_dt - today).days
        
        if diff < 0:
            return "CRITIQUE : Obsolète", 0, ref_date
        elif diff < 180:
            return "WARNING : Fin proche", 1, ref_date
        else:
            return "OK : Supporté", 2, ref_date
    except:
        return "Erreur Date", 3, ref_date

def audit_obsolescence(apps_scannees):
    """
    Compare le scan au référentiel.
    Gère deux types de vérifications : 'OS' et 'Logiciel'.
    """
    if not os.path.exists(Fichier_EOL):
        print(f"[ERREUR] Fichier {Fichier_EOL} manquant.")
        return []

    # 1. Chargement du CSV
    ref_eol = []
    try:
        with open(Fichier_EOL, mode='r', encoding='utf-8') as f:
            # On ignore les lignes vides ou commentaires
            filtered = filter(lambda row: row.strip() and not row.startswith('#'), f)
            ref_eol = list(csv.DictReader(filtered, delimiter=';'))
    except Exception as e:
        print(f"[ERREUR] Lecture CSV : {e}")
        return []

    results = []
    machine_name = platform.node()
    
    # 2. Vérification de l'OS (Une seule fois)
    current_os_string = OS_Info() # Ex: "Windows 10"
    
    for ref in ref_eol:
        # --- CAS 1 : Vérification de l'OS ---
        if ref['type'] == 'OS':
            # Si la version de ref (ex: "10") est dans la chaine système (ex: "Windows 10")
            if ref['version'].lower() in current_os_string.lower():
                statut, level, date = verifier_date(ref['eol_date'])
                results.append({
                    "machine": machine_name,
                    "type": "OS",
                    "composant": current_os_string,
                    "eol": date,
                    "statut": statut,
                    "niveau": level
                })

        # --- CAS 2 : Vérification des Logiciels ---
        elif ref['type'] == 'Logiciel':
            for app in apps_scannees:
                # Si la version de ref (ex: "Firefox 115") est dans l'app installée
                if ref['version'].lower() in app['version'].lower():
                    statut, level, date = verifier_date(ref['eol_date'])
                    results.append({
                        "machine": machine_name,
                        "type": "Logiciel",
                        "composant": app['version'],
                        "eol": date,
                        "statut": statut,
                        "niveau": level
                    })
                    # On break pour éviter les doublons sur une même règle
                    break 

    # Tri par gravité (0 = Critique en haut)
    results.sort(key=lambda x: x['niveau'])
    return results

def generer_rapports(results):
    """Génère CSV et JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_fn = f"{Fichier_Rapport_Final}_{timestamp}.csv"
    json_fn = f"{Fichier_Rapport_Final}_{timestamp}.json"

    if results:
        with open(csv_fn, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(results)

    report_data = {
        "date_audit": datetime.now().isoformat(),
        "stats": {
            "critique": len([r for r in results if r['niveau'] == 0]),
            "warning": len([r for r in results if r['niveau'] == 1]),
            "ok": len([r for r in results if r['niveau'] == 2])
        },
        "details": results
    }
    with open(json_fn, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)

    return csv_fn, json_fn

def start_audit():
    print("\n--- AUDIT D'OBSOLESCENCE ---")
    print(f"[*] Chargement du référentiel : {Fichier_EOL}")
    
    # Scan
    print("[*] Scan système et applications...")
    apps = scanner_applications_locales()
    
    # Audit
    print("[*] Comparaison en cours...")
    audit_results = audit_obsolescence(apps)
    
    if audit_results:
        c, j = generer_rapports(audit_results)
        
        crit = len([r for r in audit_results if r['niveau'] == 0])
        warn = len([r for r in audit_results if r['niveau'] == 1])
        
        print("\n" + "="*40)
        print(f"RÉSULTAT : {crit} CRITIQUE(S) / {warn} WARNING(S)")
        for item in audit_results:
            # Affichage simplifié dans la console
            icon = "[!]" if item['niveau'] == 0 else "[i]"
            print(f"{icon} {item['type']} : {item['composant']} -> {item['statut']} (EOL: {item['eol']})")
            
        print("-" * 40)
        print(f"Rapports générés : {c}, {j}")
        print("="*40)
    else:
        print("\n[OK] Aucun élément du référentiel trouvé sur cette machine.")
    
    input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    start_audit()