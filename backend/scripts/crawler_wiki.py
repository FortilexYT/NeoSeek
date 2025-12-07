import wikipediaapi
import requests
import time
import re
import datetime

# --- CONFIGURATION COMMUNE ---
MEILI_URL = "http://127.0.0.1:7700"
MEILI_KEY = "rVR_Z3zs5Ah3zwbrhj1HL7SgxoCssmdBiQd6A1Coj4" 
WIKI_PAGES_LIMIT = 500

def log_status(crawler_type, status, message):
    """[h:m:s] [TYPE] [ÉTAT] Message"""
    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
    print(f"{timestamp} [{crawler_type}] [{status}] {message}")

def send_to_meilisearch(documents):
    """Fonction utilitaire pour envoyer un lot de documents à Meilisearch."""
    if not documents:
        return
    # [Log de la tentative d'envoi omis pour garder la console propre]
    try:
        requests.post(
            f"{MEILI_URL}/indexes/docs/documents",
            headers={"Authorization": f"Bearer {MEILI_KEY}", "Content-Type": "application/json"},
            json=documents
        )
    except Exception as e:
        print(f"   X Erreur de connexion Meilisearch: {e}")

def is_already_indexed(title, crawler_id):
    """Vérifie si un document avec ce titre existe déjà dans Meilisearch."""
    try:
        res = requests.post(
            f"{MEILI_URL}/indexes/docs/search",
            headers={
                "Authorization": f"Bearer {MEILI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "filter": [f"title = \"{title.replace('"', '\\"')}\""],
                "limit": 1
            }
        )
        if res.ok:
            data = res.json()
            if data['estimatedTotalHits'] > 0:
                return True
    except Exception as e:
        log_status(crawler_id, "ERREUR REQ", f"Meilisearch check failed: {e}")
    return False

def crawl_wikipedia(start_page_titles, crawler_id):
    """
    Crawler spécialisé dans l'API Wikipédia avec calcul SRAS.
    """
    wiki = wikipediaapi.Wikipedia(
        user_agent=f'NeoSeekBot/{crawler_id} (SRAS Mode)',
        language='fr'
    )
    
    documents = []
    visited_titles = set()
    to_visit_queue = list(start_page_titles)
    
    log_status(crawler_id, "DÉMARRAGE", f"Pages de départ : {start_page_titles}")

    count_indexed = 0
    
    while to_visit_queue and count_indexed < WIKI_PAGES_LIMIT:
        titre = to_visit_queue.pop(0)

        if titre in visited_titles:
            log_status(crawler_id, "SKIP (VU)", f"Titre déjà visité dans la session: {titre}")
            continue
        
        # --- VÉRIFICATION D'EXISTENCE DANS MEILISEARCH ---
        if is_already_indexed(titre, crawler_id):
            visited_titles.add(titre)
            log_status(crawler_id, "SKIP (DB)", f"Titre déjà dans la base de données: {titre}")
            continue
        # ------------------------------------------------

        if re.match(r'^\d{1,2} [a-z]+', titre):
            log_status(crawler_id, "SKIP (FILTRE)", f"Ignoré (date/format): {titre}")
            continue

        try:
            page = wiki.page(titre)
            if not page.exists(): 
                log_status(crawler_id, "SKIP (404)", f"Page introuvable: {titre}")
                continue
            
            if len(page.summary) < 100: 
                log_status(crawler_id, "SKIP (COURT)", f"Résumé trop court: {titre}")
                continue

            link_count = len(page.links)
            
            doc = {
                "id": f"WIKI-{int(time.time() * 1000) + count_indexed}",
                "url": page.fullurl,
                "title": page.title,
                "content": page.summary,
                "internal_link_count": link_count
            }
            
            documents.append(doc)
            visited_titles.add(titre)
            count_indexed += 1
            
            log_status(crawler_id, "INDEXÉ", f"SRAS: {link_count} - {doc['title']} ({count_indexed}/{WIKI_PAGES_LIMIT})")
            
            # Ajoutez de nouveaux liens à explorer
            for link_title, link_obj in page.links.items():
                if link_obj.namespace == wikipediaapi.Namespace.MAIN and link_title not in visited_titles:
                    to_visit_queue.append(link_title)

            if len(documents) >= 20:
                send_to_meilisearch(documents)
                documents = [] 
            
            time.sleep(0.1)

        except Exception as e:
            log_status(crawler_id, "ERREUR", f"Erreur de traitement: {e} sur {titre}")
            continue

    send_to_meilisearch(documents)
    log_status(crawler_id, "TERMINÉ", f"{count_indexed} documents indexés.")