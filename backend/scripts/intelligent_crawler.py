import requests
from bs4 import BeautifulSoup
import time
import re
import random
import datetime
import urllib.parse
import threading
import concurrent.futures
from queue import Queue
from langdetect import detect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION ---
MEILI_URL = "http://127.0.0.1:7700"
MEILI_KEY = "rVR_Z3zs5Ah3zwbrhj1HL7SgxoCssmdBiQd6A1Coj4"
USER_AGENT = {'User-Agent': 'Mozilla/5.0 (compatible; NeoSeekBot/4.0; +http://neoseek.org)'}
NUM_THREADS = 10  # Nombre de robots simultanés

# --- LISTE NOIRE ---
BLOCKED_DOMAINS = [
    "facebook", "twitter", "instagram", "tiktok", "linkedin", "pinterest", "youtube",
    "porn", "xxx", "hentai", "sex", "escort", "cam", "betting", "casino", "poker",
    "viagra", "cialis", "pharma", "warez", "crack", "hack", "torrent",
    "login", "signup", "signin", "register", "cart", "checkout", "shop"
]
BLOCKED_KEYWORDS = ["adult only", "18+", "jeu d'argent", "dating", "rencontre", "sex"]

# Verrou pour la synchronisation des threads
lock = threading.Lock()

# --- MODULE 1 : ANALYSE SÉMANTIQUE ---
class SemanticBrain:
    def __init__(self):
        print("[SYSTEM] Initialisation du module d'analyse sémantique...")
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.seed_matrix = None
        self.seeds = [
            "https://fr.wikipedia.org/wiki/Science",
            "https://www.lemonde.fr",
            "https://www.bbc.com"
        ]

    def train(self):
        contents = []
        for url in self.seeds:
            try:
                r = requests.get(url, headers=USER_AGENT, timeout=3)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    contents.append(soup.get_text(" ", strip=True)[:4000])
            except: pass
        
        if contents:
            self.seed_matrix = self.vectorizer.fit_transform(contents)
            print("[SYSTEM] Calibrage IA termine. Filtre actif.")
        else:
            print("[WARNING] Echec du calibrage IA. Mode permissif.")

    def is_informative(self, text):
        if self.seed_matrix is None: return True, 0.5
        try:
            vec = self.vectorizer.transform([text])
            score = cosine_similarity(vec, self.seed_matrix).mean()
            return score > 0.05, score
        except: return False, 0.0

# --- MODULE 2 : SÉCURITÉ ---
class SecurityGuard:
    def check_url(self, url):
        url_l = url.lower()
        if url_l.endswith(('.jpg', '.png', '.pdf', '.zip', '.css', '.js', '.xml')): return False
        if any(bad in url_l for bad in BLOCKED_DOMAINS): return False
        return True

    def check_content(self, text):
        text_l = text.lower()
        if any(bad in text_l for bad in BLOCKED_KEYWORDS): return False
        return True

# --- MODULE 3 : MOTEUR MULTI-THREAD ---
class TurboExplorer:
    def __init__(self):
        self.brain = SemanticBrain()
        self.guard = SecurityGuard()
        self.brain.train()
        
        self.queue = Queue()
        
        seeds = [
            "https://fr.wikipedia.org/wiki/Sp%C3%A9cial:Page_au_hasard",
            "https://www.lemonde.fr/actualite-en-continu/",
            "https://news.google.com/",
            "https://korben.info/",
            "https://www.futura-sciences.com/"
        ]
        for s in seeds: self.queue.put(s)
        
        self.visited = set()
        self.indexed_count = 0
        self.max_pages = 0

    def extract_links(self, soup, base_url):
        new_links = []
        try:
            for a in soup.find_all('a', href=True, limit=50):
                link = a['href']
                full = urllib.parse.urljoin(base_url, link)
                if full.startswith('http') and self.guard.check_url(full):
                    new_links.append(full)
        except: pass
        return new_links

    def process_url(self, url):
        with lock:
            if self.indexed_count >= self.max_pages: return
            if url in self.visited: return
            self.visited.add(url)
            # Affichage discret de l'activité
            print(f">>> Analysing: {url[:60]}...", end='\r')

        try:
            resp = requests.get(url, headers=USER_AGENT, timeout=3)
            if resp.status_code != 200: return

            soup = BeautifulSoup(resp.text, 'html.parser')
            for x in soup(['script', 'style', 'nav', 'footer']): x.extract()
            text = soup.get_text(" ", strip=True)
            title = soup.title.string.strip() if soup.title else url

            if len(text) < 400: return
            
            if not self.guard.check_content(text): return
            try:
                if detect(text) not in ['fr', 'en']: return
            except: return
            
            is_good, score = self.brain.is_informative(text)
            
            if is_good:
                doc = {
                    "id": f"fast-{int(time.time()*100000)}",
                    "url": url,
                    "title": title,
                    "content": text[:8000],
                    "ai_score": float(score),
                    "indexed_at": datetime.datetime.now().isoformat()
                }
                
                try:
                    requests.post(
                        f"{MEILI_URL}/indexes/docs/documents",
                        headers={"Authorization": f"Bearer {MEILI_KEY}"},
                        json=[doc]
                    )
                    with lock:
                        self.indexed_count += 1
                        # Log de succès propre et aligné
                        print(f"[+] [{self.indexed_count}/{self.max_pages}] INDEXED | Score: {score:.2f} | {title[:40]}")
                except: pass

            links = self.extract_links(soup, url)
            random.shuffle(links)
            for l in links[:5]:
                self.queue.put(l)

        except Exception:
            pass

    def start_turbo(self, limit=100):
        self.max_pages = limit
        print(f"\n[INFO] Demarrage du crawler | Threads: {NUM_THREADS} | Objectif: {limit} pages")
        print("-" * 70)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            while self.indexed_count < self.max_pages:
                if self.queue.empty():
                    time.sleep(1)
                    continue
                
                futures = []
                for _ in range(NUM_THREADS):
                    if not self.queue.empty() and self.indexed_count < self.max_pages:
                        url = self.queue.get()
                        futures.append(executor.submit(self.process_url, url))
                
                concurrent.futures.wait(futures)

        print("-" * 70)
        print("[INFO] Operation terminee.")

if __name__ == "__main__":
    bot = TurboExplorer()
    try:
        q = input("Nombre de pages a indexer (defaut 100) : ")
        limit = int(q)
    except:
        limit = 100
        
    bot.start_turbo(limit)