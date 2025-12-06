from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import time
import re
import sys
import random

# --- CONFIGURATION MEILISEARCH ---
MEILI_URL = "http://127.0.0.1:7700"
MEILI_KEY = "rVR_Z3zs5Ah3zwbrJhj1HL7SgxoCssmdBiQd6A1Coj4"

# Liste noire (Anti-Pub/Forum/Réseaux sociaux)
BLOCKED_DOMAINS = [
    "facebook", "twitter", "instagram", "tiktok", "reddit", "quora", "zhihu", "baidu", 
    "pinterest", "linkedin", "forum", "thread", "discussion", "login", "signup", "shopping", "amazon", "ebay"
]

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def is_safe_url(url):
    for blocked in BLOCKED_DOMAINS:
        if blocked in url.lower():
            return False
    return True

# --- INTERACTION UTILISATEUR ---
print("\n🔎 --- NEOSEEK WEB CRAWLER (Mode Manuel) ---")
try:
    sujet_demande = input(">> Quel est le thème de ta recherche ? : ").strip()
    if not sujet_demande:
        print("❌ Tu dois entrer un sujet !")
        sys.exit()

    nb_pages_str = input(">> Combien de pages veux-tu analyser ? (ex: 20, 50, 100) : ").strip()
    try:
        LIMIT_PAGES = int(nb_pages_str)
    except ValueError:
        print("⚠️ Nombre invalide, on part sur 20 pages par défaut.")
        LIMIT_PAGES = 20

except KeyboardInterrupt:
    print("\n👋 Arrêt demandé.")
    sys.exit()

# --- DÉBUT DU TRAITEMENT ---
print(f"\n🚀 Lancement de la recherche sur : '{sujet_demande}' ({LIMIT_PAGES} pages max)")
print("-" * 50)

urls_to_scan = []

# 1. Recherche DuckDuckGo
try:
    with DDGS() as ddgs:
        print(f"   🔎 Interrogation du moteur de recherche...")
        # On demande un peu plus de résultats que prévu car on va en filtrer certains
        results = list(ddgs.text(sujet_demande, region='fr-fr', max_results=LIMIT_PAGES + 10))
        
        for r in results:
            if is_safe_url(r['href']):
                urls_to_scan.append({'url': r['href'], 'title': r['title']})
                # On s'arrête dès qu'on a le nombre demandé
                if len(urls_to_scan) >= LIMIT_PAGES:
                    break
        
        print(f"   ✅ {len(urls_to_scan)} liens pertinents trouvés.")

except Exception as e:
    print(f"[ERREUR] DuckDuckGo n'a pas répondu : {e}")
    sys.exit()

documents = []
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

# 2. Visite des sites
print(f"   🚀 Aspiration en cours (Cela peut prendre un moment...)\n")

for i, page_info in enumerate(urls_to_scan):
    url = page_info['url']
    titre_brut = page_info['title']

    try:
        # Timeout de 6 secondes
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code != 200: continue

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Nettoyage
        for junk in soup(["script", "style", "nav", "footer", "header", "form", "aside", "noscript"]):
            junk.extract()

        # Extraction intelligente (Main ou Body)
        main_content = soup.find('main') or soup.find('article') or soup.body
        if not main_content: continue
        
        raw_text = main_content.get_text(" ", strip=True)
        clean_content = clean_text(raw_text)

        # Filtre qualité : on ignore les pages trop vides (< 400 caractères)
        if len(clean_content) < 400: 
            print(f"   -> [IGNORÉ] Trop court : {titre_brut[:30]}...")
            continue

        # Création Document
        doc = {
            "id": int(time.time() * 10000) + i + random.randint(1,9999), 
            "url": url,
            "title": soup.title.string.strip() if soup.title else titre_brut,
            "content": clean_content[:9000] # On garde jusqu'à 9000 caractères
        }
        documents.append(doc)
        
        print(f"   -> [{i+1}/{len(urls_to_scan)}] Indexé : {doc['title'][:50]}...")

    except Exception as e:
        # On ignore silencieusement les erreurs pour ne pas polluer l'affichage
        continue

# 3. Envoi Meilisearch
print("-" * 50)
if documents:
    print(f"📤 Envoi de {len(documents)} documents vers NeoSeek...")
    try:
        res = requests.post(
            f"{MEILI_URL}/indexes/docs/documents",
            headers={"Authorization": f"Bearer {MEILI_KEY}"},
            json=documents
        )
        if res.status_code in [200, 201, 202]:
            print(f"🎉 SUCCÈS ! Les connaissances sur '{sujet_demande}' sont ajoutées.")
        else:
            print(f"⚠️ Erreur Meilisearch code : {res.status_code}")
    except Exception as e:
        print(f"❌ Erreur Envoi : {e}")
else:
    print("❌ Aucun document valide n'a pu être récupéré.")