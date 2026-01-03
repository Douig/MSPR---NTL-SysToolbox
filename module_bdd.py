# Fichier : module_bdd.py
import mysql.connector
import csv
import os
import datetime
import json

# --- CONFIGURATION GLOBALE ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root", 
    "database": "demo_db"
}

# --- CONFIGURATION DES DOSSIERS ---
DOSSIER_EXPORTS = "exports_csv_wms"
DOSSIER_BACKUPS = "backups_sql"
DOSSIER_JSON = "rapports_json"   

# Création automatique des dossiers si inexistants

os.makedirs(DOSSIER_EXPORTS, exist_ok=True)
os.makedirs(DOSSIER_BACKUPS, exist_ok=True)
os.makedirs(DOSSIER_JSON, exist_ok=True) 

# --- FONCTIONS UTILITAIRES ---

def connect_db():
    """Gère la connexion à la BDD de manière sécurisée."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        return None

def ts():
    """Génère un timestamp pour nommer les fichiers."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# --- 1. FONCTIONNALITÉS JSON (DIAGNOSTIC) ---

def generate_status_json():
    """
    Récupère les métriques de la BDD et retourne une chaîne JSON.
    """
    response = {
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "MySQL/MariaDB",
        "host": DB_CONFIG["host"],
        "database": DB_CONFIG["database"]
    }

    conn = connect_db()
    
    if conn:
        try:
            cursor = conn.cursor()
            
            # Récupérer la version
            cursor.execute("SELECT VERSION()")
            response["version"] = cursor.fetchone()[0]
            
            # Récupérer les métriques
            metrics_to_check = ['Uptime', 'Threads_connected', 'Questions', 'Bytes_received', 'Bytes_sent']
            stats = {}
            for metric in metrics_to_check:
                cursor.execute(f"SHOW GLOBAL STATUS LIKE '{metric}'")
                row = cursor.fetchone()
                if row:
                    stats[metric] = row[1]
            
            response["status"] = "UP"
            response["metrics"] = stats
            conn.close()
            
        except Exception as e:
            response["status"] = "ERROR"
            response["error_details"] = str(e)
    else:
        response["status"] = "DOWN"
        response["error_details"] = "Impossible de se connecter au serveur"

    return json.dumps(response, indent=4)

def save_json_report(json_str):
    """
    Sauvegarde la chaîne JSON dans un fichier daté.
    """
    try:
        filename = os.path.join(DOSSIER_JSON, f"status_mysql_{ts()}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json_str)
            
        return filename
    except Exception as e:
        print(f"Erreur lors de la sauvegarde JSON : {e}")
        return None

# --- 2. FONCTIONNALITÉ EXPORT CSV ---

def export_table_csv():
    conn = connect_db()
    if not conn:
        print("Erreur de connexion BDD.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]

        if not tables:
            print("Aucune table trouvée.")
            return

        print("\n--- TABLES DISPONIBLES (POUR CSV) ---")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")

        choix = input("\nNuméro de la table : ")
        if not choix.isdigit() or not (1 <= int(choix) <= len(tables)):
            print("Choix invalide.")
            return

        table = tables[int(choix) - 1]
        fichier_csv = os.path.join(DOSSIER_EXPORTS, f"{table}_{ts()}.csv")

        cursor.execute(f"SELECT * FROM `{table}`")
        
        with open(fichier_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            colonnes = [col[0] for col in cursor.description]
            writer.writerow(colonnes)
            writer.writerows(cursor.fetchall())

        print(f"Export CSV terminé : {fichier_csv}")

    except Exception as e:
        print(f"Erreur export : {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

# --- 3. FONCTIONNALITÉ BACKUP SQL ---

def backup_sql_manager():
    conn = connect_db()
    if not conn:
        print("Erreur de connexion BDD.")
        return

    print("\n--- TYPE DE BACKUP SQL ---")
    print("1. Sauvegarder une seule table")
    print("2. Sauvegarder TOUTE la base")
    c = input(">> ")

    try:
        cursor = conn.cursor()
        
        if c == "1":
            cursor.execute("SHOW TABLES")
            tables = [t[0] for t in cursor.fetchall()]
            
            for i, t in enumerate(tables, 1):
                print(f"{i}. {t}")
            
            choix = input("Numéro de la table : ")
            if choix.isdigit() and (1 <= int(choix) <= len(tables)):
                table = tables[int(choix)-1]
                filename = os.path.join(DOSSIER_BACKUPS, f"{table}_{ts()}.sql")
                
                with open(filename, "w", encoding="utf-8") as f:
                    cursor.execute(f"SHOW CREATE TABLE `{table}`")
                    f.write(cursor.fetchone()[1] + ";\n\n")
                    cursor.execute(f"SELECT * FROM `{table}`")
                    for row in cursor.fetchall():
                        values = ", ".join(f"'{str(v)}'" for v in row)
                        f.write(f"INSERT INTO `{table}` VALUES ({values});\n")
                print(f"Backup Table terminé : {filename}")

        elif c == "2":
            filename = os.path.join(DOSSIER_BACKUPS, f"FULL_DB_{ts()}.sql")
            with open(filename, "w", encoding="utf-8") as f:
                cursor.execute("SHOW TABLES")
                tables = [t[0] for t in cursor.fetchall()]
                for table in tables:
                    cursor.execute(f"SHOW CREATE TABLE `{table}`")
                    f.write(cursor.fetchone()[1] + ";\n\n")
                    cursor.execute(f"SELECT * FROM `{table}`")
                    for row in cursor.fetchall():
                        values = ", ".join(f"'{str(v)}'" for v in row)
                        f.write(f"INSERT INTO `{table}` VALUES ({values});\n")
                    f.write("\n\n")
            print(f"Backup Complet terminé : {filename}")
            
    except Exception as e:
        print(f"Erreur Backup : {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

# --- 4. MENU EXPORT & BACKUP (Appelé par le main.py) ---

def menu_export_backup():
    """
    Ce menu gère uniquement les actions d'export et de sauvegarde.
    """
    while True:
        print("\n--- EXPORT ET BACKUP BDD ---")
        print("1. Exporter une table en CSV")
        print("2. Gestion des Backups SQL")
        print("3. Retour au menu principal")
        
        c = input(">> ")
        
        if c == "1":
            export_table_csv()
            generate_and_save_json_report()  
        elif c == "2":
            backup_sql_manager()
            generate_and_save_json_report()  
        elif c == "3":
            break 
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    menu_export_backup()

# --- 5. GÉNÉRATION ET SAUVEGARDE DU RAPPORT JSON ---

def generate_and_save_json_report():
    """
    Génère le diagnostic JSON de la BDD et le sauvegarde dans un fichier.
    """
    json_data = generate_status_json()
    fichier = save_json_report(json_data)

    if fichier:
        print(f"Rapport JSON généré avec succès : {fichier}")
    else:
        print("Échec de la génération du rapport JSON")
 