import multiprocessing
import time
from crawler_wiki import crawl_wikipedia
from crawler_web_thematic import crawl_web_topic

# --- CONFIGURATION DES 5 CRAWLERS ---
CRAWLER_TASKS = [
    # 1. CRAWLER WIKIPEDIA (Autorité SRAS)
    {
        "type": "wiki",
        "name": "WIKI-1",
        # Pages de départ pour une exploration ciblée
        "args": (["Intelligence artificielle", "Crise climatique", "Technologies de l'information"], "WIKI-1")
    },
    
    # 2. CRAWLERS ACTUALITÉS (2 Processus)
    {
        "type": "web",
        "name": "ACTU-1",
        # Thème spécifique pour ce processus
        "args": ("Actualités politiques et économiques récentes France", "ACTU-1", 100) 
    },
    {
        "type": "web",
        "name": "ACTU-2",
        "args": ("Dernières nouvelles scientifiques et médicales", "ACTU-2", 100)
    },

    # 3. CRAWLERS DIVERTISSEMENT (2 Processus)
    {
        "type": "web",
        "name": "DIVERT-1",
        "args": ("Nouveautés films et séries télévisées 2024", "DIVERT-1", 75)
    },
    {
        "type": "web",
        "name": "DIVERT-2",
        "args": ("Actualités des jeux vidéo et e-sport", "DIVERT-2", 75)
    }
]

def main():
    print("🎬 DÉMARRAGE DE NEOSEEK - 5 CRAWLERS EN PARALLÈLE")
    processes = []
    
    # Création des processus
    for task in CRAWLER_TASKS:
        if task["type"] == "wiki":
            p = multiprocessing.Process(target=crawl_wikipedia, args=task["args"])
        elif task["type"] == "web":
            p = multiprocessing.Process(target=crawl_web_topic, args=task["args"])
        
        processes.append(p)
        p.start()
        # Petite pause pour éviter une saturation immédiate au démarrage
        time.sleep(0.5) 

    # Attente de la fin de tous les processus
    for p in processes:
        p.join()

    print("\n TOUS LES CRAWLERS ONT TERMINÉ LEUR TÂCHE.")
    print("Projet NeoSeek mis à jour avec la nouvelle stratégie d'exploration.")

if __name__ == '__main__':
    main()