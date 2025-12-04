def menu_diagnostics():
    """
    Ceci est le sous-menu. On y reste tant qu'on ne demande pas le retour.
    """
    sous_running = True
    while sous_running:
        print("\n--- DIAGNOSTIC SYSTEME ---")
        print("1. Supervision Hardware Linux (CPU/RAM)")
        print("2. Statut MySQL")
        print("3. Test AD/DNS")
        print("4. Retour au menu principal")
        
        sub_choix = input(">> ")

        if sub_choix == "1":
            print("Lancement du check Hardware...")
            # Ici tu appelleras plus tard ta fonction get_system_metrics()
            
        elif sub_choix == "2":
            print("Vérification MySQL...")
            
        elif sub_choix == "3":
            print("Test Réseau...")
            
        elif sub_choix == "4":
            print("Retour...")
            return  # <--- C'est la clé ! Ça arrête la fonction et revient au code principal
            
        else:
            print("Choix invalide.")

