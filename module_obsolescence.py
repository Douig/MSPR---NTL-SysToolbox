import sys
import platform
import csv
import json
import os
import subprocess
import re
from datetime import datetime

# --- CONFIGURATION ---
Fichier_EOL = "eol_reference.csv"
Fichier_Inventaire = "inventaire_complet.csv" # Scan brut
Fichier_Rapport_Final = "rapport_audit"        # Nom de base des rapports

def OS_Info():
    """Identifie l'OS et la version précise"""
    os_name = "Windows" if sys.platform == "win32" else "Linux"
    version = platform.release()
    if os_name == "Linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        version = line.split("=")[1].strip().strip('"')
        except:
            version = platform.version()
    return {"os": os_name, "version": version}

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
                            version = "Indéterminée"
                        apps.append({"nom_machine": nom_machine, "version": f"{name} {version}"})
                    except: continue
            except: continue
    else:
        # Scan pour Linux (Debian/Ubuntu)
        try:
            result = subprocess.check_output(["dpkg-query", "-W", "-f=${Package};${Version}\n"], text=True)
            for line in result.strip().split('\n'):
                name, ver = line.split(';')
                apps.append({"nom_machine": nom_machine, "version": f"{name} {ver}"})
        except: pass
    return apps

def audit_obsolescence(apps_scannees):
    """Compare le scan au référentiel et FILTRE les inconnus"""
    if not os.path.exists(Fichier_EOL):
        print(f"Erreur : Le fichier {Fichier_EOL} est introuvable.")
        return []

    # Chargement du référentiel (Liste Blanche)
    ref_eol = []
    with open(Fichier_EOL, mode='r', encoding='utf-8') as f:
        # On filtre les lignes de commentaires commençant par '#'
        filtered_f = filter(lambda row: row.strip() and not row.startswith('#'), f)
        ref_eol = list(csv.DictReader(filtered_f, delimiter=';'))

    results = []
    today = datetime.now().date()

    for app in apps_scannees:
        for ref in ref_eol:
            # Match partiel : On vérifie si le nom simplifié est dans le nom complet
            if ref['version'].lower() in app['version'].lower():
                try:
                    eol_dt = datetime.strptime(ref['eol_date'], "%Y-%m-%d").date()
                    diff = (eol_dt - today).days
                    
                    status = "OK : Supporté"
                    level = 2
                    if diff < 0:
                        status = "CRITIQUE : Obsolète"
                        level = 0
                    elif diff < 180:
                        status = "WARNING : Fin proche"
                        level = 1

                    results.append({
                        "machine": app['nom_machine'],
                        "composant": app['version'],
                        "eol": ref['eol_date'],
                        "statut": status,
                        "niveau": level
                    })
                    break # On arrête de chercher pour cette application dès qu'un match est trouvé
                except:
                    continue
    
    # Tri par gravité (Critique en premier)
    results.sort(key=lambda x: x['niveau'])
    return results

def generer_rapports(results):
    """Génère les livrables CSV et JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_fn = f"{Fichier_Rapport_Final}_{timestamp}.csv"
    json_fn = f"{Fichier_Rapport_Final}_{timestamp}.json"

    # Rapport CSV
    if results:
        with open(csv_fn, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(results)

    # Rapport JSON
    report_data = {
        "date_audit": datetime.now().isoformat(),
        "stats": {
            "total_critique": len([r for r in results if r['niveau'] == 0]),
            "total_warning": len([r for r in results if r['niveau'] == 1]),
            "total_ok": len([r for r in results if r['niveau'] == 2])
        },
        "details": results
    }
    with open(json_fn, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)

    return csv_fn, json_fn

if __name__ == "__main__":
    print("--- NTL-SysToolbox : Audit d'Obsolescence Filtré ---")
    
    # 1. Info Système
    local = OS_Info()
    print(f"[*] Système détecté : {local['version']}")
    
    # 2. Scan
    raw_apps = scanner_applications_locales()
    print(f"[*] Scan terminé : {len(raw_apps)} éléments trouvés sur le système.")
    
    # 3. Audit & Filtrage
    print(f"[*] Filtrage selon {Fichier_EOL}...")
    final_audit = audit_obsolescence(raw_apps)
    
    # 4. Sortie
    if final_audit:
        c_file, j_file = generer_rapports(final_audit)
        print("\n" + "="*40)
        print(f"AUDIT TERMINÉ AVEC SUCCÈS")
        print(f"- Éléments importants suivis : {len(final_audit)}")
        print(f"- Rapport CSV : {c_file}")
        print(f"- Rapport JSON : {j_file}")
        
        # Petit résumé console
        crit = len([r for r in final_audit if r['niveau'] == 0])
        warn = len([r for r in final_audit if r['niveau'] == 1])
        print(f"\nRésumé : {crit} CRITIQUE(S), {warn} WARNING(S)")
        print("="*40)
    else:
        print("\n[!] Aucun composant du référentiel n'a été trouvé sur cette machine.")