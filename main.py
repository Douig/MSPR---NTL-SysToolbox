from fonction import menu_diagnostics
# --- BOUCLE PRINCIPALE ---
running = True

while running:
    print("\n------ NTL-SysToolbox ------")
    print("1. Menu Diagnostic")
    print("2. Quitter")
    print("----------------------------")
    
    choix = input(">> ").lower()
    
    if choix in ["1", "menu", "1."]:
        # Au lieu d'afficher du texte, on SAUTE dans la fonction du sous-menu
        menu_diagnostics()
        # Quand le "return" du sous-menu sera activé, le code reprendra ICI
        
    elif choix in ["2", "quitter", "2."]:
        print("Fermeture de l'application.")
        running = False
    else:
        print("Erreur : valeur incorrect.")