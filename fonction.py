# Fichier : fonction.py
from module_systeme import monitor_linux, monitor_windows
from module_bdd import generate_status_json, save_json_report 

def menu_diagnostics():
    sous_running = True
    
    while sous_running:
        print("\n--- DIAGNOSTIC SYSTEME ---")
        print("1. Supervision Hardware (Choix OS)")
        print("2. Statut Base de Données (JSON)")
        print("3. Retour")
        print("--------------------------")
        
        sub_choix = input(">> ").lower()

        if sub_choix == "1":
            # Sous-menu sélection OS
            print("\nCible de l'analyse :")
            print("1. Linux")
            print("2. Windows (Placeholder)")
            print("3. Annuler")
            
            os_choix = input(">> ")
            
            if os_choix == "1":
                monitor_linux()
            elif os_choix == "2":
                monitor_windows()
            elif os_choix == "3":
                pass
            else:
                print("Choix invalide.")
            
        elif sub_choix == "2":
            # Génération et sauvegarde rapport JSON
            print("\n--- STATUT MYSQL (JSON) ---")
            json_output = generate_status_json()
            print(json_output)
            
            save = input("\nSauvegarder ? (o/n) : ")
            if save.lower() == "o":
                fichier = save_json_report(json_output)
                if fichier:
                    print(f"Sauvegarde : {fichier}")
            input("\nEntrée pour continuer...")
            
        elif sub_choix == "3":
            return 
            
        else:
            print("Saisie invalide.")