import mysql.connector
import os
import csv

# Connexion à la base MySQL
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="demo_db"
    )
    mycursor = mydb.cursor()
except mysql.connector.Error as err:
    print(f"Erreur de connexion : {err}")
    exit(1)


# Dossier pour stockés les CSV

DOSSIER_EXPORTS = "exports_csv_wms"
os.makedirs(DOSSIER_EXPORTS, exist_ok=True)


def export_table_csv():
    print("\n--- Export CSV ---")

    try:
        # Recup des tables
        mycursor.execute("SHOW TABLES")
        tables = [t[0] for t in mycursor.fetchall()]

        if not tables:
            print("Aucune table trouvée.")
            return 1

        # Affichage des tables
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")

        choix = input("\nNuméro de la table : ")

        if not choix.isdigit() or not (1 <= int(choix) <= len(tables)):
            print("Choix invalide.")
            return 1

        table = tables[int(choix) - 1]

        # Nomination des fichiers csv
        fichier_csv = os.path.join(DOSSIER_EXPORTS, f"{table}_csv.csv")

        # recup des donnee
        mycursor.execute(f"SELECT * FROM `{table}`")

        # Écriture du fichier
        with open(fichier_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")

            # En-tête
            colonnes = [col[0] for col in mycursor.description]
            writer.writerow(colonnes)

            # Données
            writer.writerows(mycursor.fetchall())

        print(f"Export terminé : {fichier_csv}")
        return 0

    except Exception as e:
        print(f"Erreur export : {e}")
        return 1


# menu 
def main_menu():
    while True:
        print("\n===== MENU =====")
        print("1. Exporter une table en CSV")
        print("0. Quitter")

        choix = input("Votre choix : ")

        if choix == "1":
            export_table_csv()
        elif choix == "0":
            print("Fin du programme.")
            break
        else:
            print("Choix incorrect.")


if __name__ == "__main__":
    main_menu()

    # Fermeture de la connexion
    if mydb.is_connected():
        mycursor.close()
        mydb.close()
