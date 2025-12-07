from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import time
import re
import random
import datetime

# --- CONFIGURATION COMMUNE ---
MEILI_URL = "http://127.0.0.1:7700"
MEILI_KEY = "rVR_Z3zs5Ah3zwbrhj1HL7SgxoCssmdBiQd6A1Coj4"
USER_AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
# Liste noire (Anti-Pub/Forum/Réseaux sociaux)
BLOCKED_DOMAINS = [
    "facebook", "twitter", "instagram", "tiktok", "reddit", "quora", "zhihu", "baidu", 
    "pinterest", "linkedin", "forum", "thread", "discussion", "login", "signup", "shopping", "amazon", "ebay"
]

def log_status(crawler_type, status, message):
    """[h:m:s] [TYPE] [ÉTAT] Message"""
    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
    print(f"{timestamp} [{crawler_type}] [{status}] {message}")

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def is_safe_url(url):
    for blocked in BLOCKED_DOMAINS:
        if blocked in url.lower():
            return False
    return True

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
        print(f"   ❌ Erreur de connexion Meilisearch: {e}")
    
def is_already_indexed(url, crawler_id):
    """Vérifie si un document avec cette URL existe déjà dans Meilisearch."""
    try:
        res = requests.post(
            f"{MEILI_URL}/indexes/docs/search",
            headers={
                "Authorization": f"Bearer {MEILI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "filter": [f"url = \"{url}\""],
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

def crawl_web_topic(sujet_demande, crawler_id, limit_pages=100):
    """
    Crawler web thématique utilisant DuckDuckGo Search et BeautifulSoup.
    """
    
    log_status(crawler_id, "DÉMARRAGE", f"Thème : '{sujet_demande}' ({limit_pages} pages max)")
    urls_to_scan = []

    # 1. Recherche DuckDuckGo
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(sujet_demande, region='fr-fr', max_results=limit_pages + 20))
            
            for r in results:
                if is_safe_url(r['href']):
                    urls_to_scan.append({'url': r['href'], 'title': r['title']})
                    if len(urls_to_scan) >= limit_pages:
                        break
            
            log_status(crawler_id, "DDGS", f"{len(urls_to_scan)} liens pertinents trouvés.")

    except Exception as e:
        log_status(crawler_id, "ERREUR DDGS", f"DuckDuckGo n'a pas répondu : {e}")
        return

    documents = []
    
    # 2. Visite des sites
    for i, page_info in enumerate(urls_to_scan):
        url = page_info['url']
        titre_brut = page_info['title']

        # --- VÉRIFICATION D'EXISTENCE DANS MEILISEARCH ---
        if is_already_indexed(url, crawler_id):
            log_status(crawler_id, "SKIP (DB)", f"URL déjà dans la base de données: {url[:50]}...")
            continue
        # ------------------------------------------------
        
        wait_time = random.uniform(2, 5) 
        time.sleep(wait_time) 

        try:
            response = requests.get(url, headers=USER_AGENT, timeout=8)
            
            if response.status_code != 200: 
                log_status(crawler_id, "SKIP (HTTP)", f"Code {response.status_code} sur: {url[:50]}...")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            for junk in soup(["script", "style", "nav", "footer", "header", "form", "aside", "noscript"]):
                junk.extract()

            main_content = soup.find('main') or soup.find('article') or soup.body
            if not main_content: continue
            
            raw_text = main_content.get_text(" ", strip=True)
            clean_content = clean_text(raw_text)

            if len(clean_content) < 400: 
                log_status(crawler_id, "SKIP (COURT)", f"Contenu trop court sur: {url[:50]}...")
                continue

            doc = {
                "id": f"WEB-{crawler_id}-{int(time.time() * 10000)}", 
                "url": url,
                "title": soup.title.string.strip() if soup.title else titre_brut,
                "content": clean_content[:9000] 
            }
            documents.append(doc)
            
            log_status(crawler_id, "INDEXÉ", f"Titre: {doc['title'][:40]}... ({i+1}/{len(urls_to_scan)})")

        except Exception as e:
            log_status(crawler_id, "ERREUR", f"Erreur de traitement sur {url[:50]}... : {e}")
            continue

    send_to_meilisearch(documents)
    log_status(crawler_id, "TERMINÉ", f"{len(documents)} documents indexés sur le thème '{sujet_demande}'.")