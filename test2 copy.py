import mysql.connector
import datetime
import os
import json


#partie json : 

def output_json(module, code, message, data=None):
    print(json.dumps({
        "timestamp": datetime.datetime.now().isoformat(),
        "module": module,
        "code": code,
        "message": message,
        "data": data or {}
    }, ensure_ascii=False))


# Connexion à la base 
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="demo_db",
)

mycursor = mydb.cursor() 

# Dossier des backups
BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

# Fonction qui retourne la date et l'heure actuelle
# Elle est utilisée pour créer des noms de fichiers uniques

def ts():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# OPTION 1 : AFFICHER UNE TABLE

def option_1():
    mycursor.execute("SHOW TABLES")
    tables = [t[0] for t in mycursor.fetchall()]

    print("\nTables disponibles :")
    for i, t in enumerate(tables, 1):
        print(f"{i}. {t}")

    choix = input("\nNuméro de la table à afficher : ")
    if not choix.isdigit() or not (1 <= int(choix) <= len(tables)):
        output_json("backup_sql", 1, "Numéro invalide") 
        return

    table = tables[int(choix)-1]

    print(f"\n Contenu de `{table}` :\n")
    mycursor.execute(f"SELECT * FROM {table}")
    for row in mycursor.fetchall():
        print(row)


# ================================================
# OPTION 2 : SAUVEGARDER UNE TABLE (SQL)
# ================================================

def option_2():
    mycursor.execute("SHOW TABLES")
    tables = [t[0] for t in mycursor.fetchall()]

    print("\nTables disponibles :")
    for i, t in enumerate(tables, 1):
        print(f"{i}. {t}")

    choix = input("\nNuméro de la table à sauvegarder : ")
    if not choix.isdigit() or not (1 <= int(choix) <= len(tables)):
        output_json("backup_sql", 1, "Numéro invalide") 
        return

    table = tables[int(choix)-1]
    filename = f"{BACKUP_DIR}/{table}_{ts()}.sql"

    with open(filename, "w", encoding="utf-8") as f:
        # Structure
        mycursor.execute(f"SHOW CREATE TABLE {table}")
        f.write(mycursor.fetchone()[1] + ";\n\n")

        # Données
        mycursor.execute(f"SELECT * FROM {table}")
        for row in mycursor.fetchall():
            values = ", ".join(f"'{str(v)}'" for v in row)
            f.write(f"INSERT INTO {table} VALUES ({values});\n")

    output_json("backup_sql", 0, "Table sauvegardée", {"table": table, "file": filename})  


# ================================================
# OPTION 3 : SAUVEGARDER TOUTE LA BDD (SQL)
# ================================================
def option_3():
    filename = f"{BACKUP_DIR}/FULL_DB_{ts()}.sql"

    with open(filename, "w", encoding="utf-8") as f:
        mycursor.execute("SHOW TABLES")
        tables = [t[0] for t in mycursor.fetchall()]

        for table in tables:
            # Structure
            mycursor.execute(f"SHOW CREATE TABLE {table}")
            f.write(mycursor.fetchone()[1] + ";\n\n")

            # Données
            mycursor.execute(f"SELECT * FROM {table}")
            for row in mycursor.fetchall():
                values = ", ".join(f"'{str(v)}'" for v in row)
                f.write(f"INSERT INTO {table} VALUES ({values});\n")
            f.write("\n\n")

    output_json("backup_sql", 0, "Sauvegarde complète réussie", {"file": filename})


# ================================================
# MENU PRINCIPAL
# ================================================
def main_menu():
    while True:
        print("\n===== MENU =====")
        print("1. Afficher une table")
        print("2. Sauvegarder une table")
        print("3. Sauvegarder toute la base")
        print("0. Quitter")

        choix = input("Votre choix : ")

        if choix == "1":
            option_1()
        elif choix == "2":
            option_2()
        elif choix == "3":
            option_3()
        elif choix == "0":
            print("Byebye")
            break
        else:
            print("Erreur : veillez changer votre choix")


if __name__ == "__main__":
    main_menu()