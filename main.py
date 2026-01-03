# Fichier : main.py
from fonction import menu_diagnostics
from module_bdd import menu_export_backup
from module_audit import start_audit 

running = True

while running:
    print("\n------ NTL-SysToolbox ------")
    print("1. Menu Diagnostic Système")
    print("2. Menu Export et Backup BDD")
    print("3. Audit Obsolescence Logicielle") 
    print("4. Quitter")
    print("----------------------------")
    
    choix = input(">> ").lower()
    
    if choix in ["1", "menu", "1."]:
        menu_diagnostics()
        
    elif choix in ["2", "bdd", "2."]:
        menu_export_backup()

    elif choix in ["3", "audit", "3."]:
        start_audit() 

    elif choix in ["4", "quitter", "4."]:
        print("Fermeture de l'application.")
        running = False
        
    else:
        print("Erreur : Choix invalide.")