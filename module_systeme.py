# Fichier : module_systeme.py

# Importation des bibliothèques nécessaires
import psutil    # Librairie interface pour récupérer les métriques hardware (CPU, RAM, Disques)
import platform  # Librairie standard pour extraire les informations du système d'exploitation (Kernel, Nom)
import time      # Gestion du temps et des timestamps (nécessaire pour le calcul de l'uptime)
import os        # Interaction avec le système de fichiers (lecture de fichiers système)

def monitor_system():
    """
    Fonction principale de récupération des métriques.
    Architecture : Collecte des données -> Traitement/Conversion -> Affichage.
    """
    print("\n--- ANALYSE EN COURS ---")
    
    # --- 1. IDENTIFICATION DU SYSTÈME D'EXPLOITATION ---
    
    # Récupération du nom générique de l'OS (ex: 'Linux', 'Windows')
    os_name = platform.system()
    # Récupération de la version exacte du noyau (Kernel) (ex: '5.15.0-56-generic')
    os_release = platform.release()
    
    try:
        # Tentative de lecture du fichier standard Linux contenant les infos de la distribution
        # Le bloc 'with' assure la fermeture automatique du fichier après lecture
        with open("/etc/os-release") as f:
            for line in f:
                # Recherche de la ligne standard définissant le nom d'affichage
                if line.startswith("PRETTY_NAME"):
                    # 1. split('=') : Séparer la clé et la valeur
                    # 2. [1] : Récupérer la partie droite (la valeur)
                    # 3. strip() : Nettoyer les espaces et sauts de ligne
                    # 4. strip('"') : Retirer les guillemets entourant le nom
                    os_name = line.split("=")[1].strip().strip('"')
                    break # Interruption de la boucle une fois l'info trouvée
    except:
        pass # Gestion silencieuse de l'erreur : conservation de la valeur par défaut 'Linux' si échec

    # --- 2. CALCUL DU TEMPS DE FONCTIONNEMENT (UPTIME) ---
    
    # Appel système pour obtenir le timestamp UNIX du dernier démarrage
    boot_time = psutil.boot_time()
    # Calcul du delta : Temps actuel (time.time) moins temps de démarrage
    uptime_seconds = time.time() - boot_time
    
    # Conversion arithmétique des secondes en heures (division entière)
    heures = int(uptime_seconds // 3600)
    # Calcul du reste de la division (Modulo) pour obtenir les minutes restantes
    minutes = int((uptime_seconds % 3600) // 60)

    # --- 3. MESURE DE LA CHARGE CPU ---
    
    # Appel bloquant : le script se met en pause pendant 1 seconde (interval=1)
    # Nécessaire pour comparer les compteurs CPU 'avant' et 'après' et déduire le % d'utilisation
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # --- 4. MÉTRIQUES DE LA MÉMOIRE VIVE (RAM) ---
    
    # Récupération d'un objet nommé contenant toutes les stats mémoire (total, available, percent, used...)
    ram = psutil.virtual_memory()
    
    # Conversion des octets en Gigaoctets (Go) : division par 1024^3 (1073741824)
    # Arrondi à 2 décimales pour la lisibilité
    ram_total = round(ram.total / (1024**3), 2) 
    ram_used = round(ram.used / (1024**3), 2)
    # Extraction directe du pourcentage calculé par le système
    ram_percent = ram.percent

    # --- 5. MÉTRIQUES DE STOCKAGE (DISQUE) ---
    
    # Analyse de l'utilisation disque sur le point de montage racine '/'
    disk = psutil.disk_usage('/')
    
    # Même logique de conversion (Octets -> Go) que pour la RAM
    disk_total = round(disk.total / (1024**3), 2)
    disk_used = round(disk.used / (1024**3), 2)
    disk_percent = disk.percent

    # --- 6. RENDU GRAPHIQUE (SORTIE STANDARD) ---
    
    print("-" * 40) # Séparateur visuel (40 tirets)
    # Utilisation de f-strings (formatage interpolé) pour injecter les variables
    print(f"OS       : {os_name} (Kernel {os_release})")
    print(f"Uptime   : {heures}h {minutes}m")
    print("-" * 40)
    print(f"CPU      : {cpu_usage}%")
    print(f"RAM      : {ram_used}Go / {ram_total}Go ({ram_percent}%)")
    print(f"Disque / : {disk_used}Go / {disk_total}Go ({disk_percent}%)")
    print("-" * 40)
    
    # Pause de l'exécution en attendant une interaction utilisateur (Entrée)
    input("\nAppuyez sur Entrée pour revenir au menu...")