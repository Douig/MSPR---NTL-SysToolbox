from Version_Windows import get_windows_version
from Uptime_Windows import get_windows_uptime
from Ressources import get_resource_usage
from Services_status import get_service_status



def menu():
    while True:
        print("\n--- NTL SysToolbox - Diagnostic Windows ---")
        print("1) Vérifier la version du système Windows")
        print("2) Vérifier l’uptime Windows")
        print("3) Vérifier l’utilisation des ressources")
        print("4) vérifier le statut des services AD/DNS")
        print("q) Quitter")
        
        
        choix = input("Choix : ").strip().lower()

        if choix == "1":
            get_windows_version()  # Appel de fonction Version
            
        elif choix == "2":
            get_windows_uptime()   # Appel de fonction Uptime
            
        elif choix == "3":
            get_resource_usage()   # Appel de fonction des ressources 
            
        elif choix == "4":
            status_dns, status_ntds = get_service_status()  #Appel de fonction des status de services
            print(f"Status DNS: {status_dns}")
            print(f"Status NTDS: {status_ntds}")
            
        elif choix == "q":
            print("Au revoir !")
            break
        else:
            print("Option invalide, recommencez.")

if __name__ == "__main__":
    menu()
