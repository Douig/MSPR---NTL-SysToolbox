from windows_diagnostic import (
    get_windows_version,
    get_windows_uptime,
    get_resource_usage,
)
from Services_status import get_service_status


def menu():
    while True:
        print("\n--- NTL SysToolbox ---")
        print("1) Diagnostic Windows")
        print("2) Diagnostic AD/DNS")
        print("q) Quitter")
        
        choix = input("Choix : ").strip().lower()

        if choix == "1":
            print("\n--- Diagnostic Windows ---")
            get_windows_version()
            get_windows_uptime()
            get_resource_usage()
            
        elif choix == "2":
            print("\n--- Diagnostic AD/DNS ---")
            status_dns, status_ntds = get_service_status()
            print(f"Status DNS: {status_dns}")
            print(f"Status NTDS: {status_ntds}")
            
        elif choix == "q":
            print("Au revoir !")
            break
        else:
            print("Option invalide, recommencez.")

if __name__ == "__main__":
    menu()
