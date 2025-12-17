# Fichier : main.py
from fonction import menu_diagnostics
from module_bdd import menu_export_backup  # <--- ON IMPORTE LE NOUVEAU MENU

running = True

while running:
    print("\n------ NTL-SysToolbox ------")
    print("1. Menu Diagnostic Système")
    print("2. Menu Export et Backup BDD") # <--- NOUVELLE OPTION
    print("3. Quitter")
    print("----------------------------")
    
    choix = input(">> ").lower()
    
    if choix in ["1", "menu", "1."]:
        menu_diagnostics()
        
    elif choix in ["2", "bdd", "2."]:
        # On lance le menu des exports/backups
        menu_export_backup()

    elif choix in ["3", "quitter", "3."]:
        print("Fermeture de l'application.")
        running = False
        
    else:
        print("Erreur : Choix invalide.")