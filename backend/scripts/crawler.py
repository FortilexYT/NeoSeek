import wikipediaapi
import requests
import time
import re

# --- CONFIGURATION MEILISEARCH ---
MEILI_URL = "http://127.0.0.1:7700"
MEILI_KEY = "rVR_Z3zs5Ah3zwbrhj1HL7SgxoCssmdBiQd6A1Coj4" # Vérifie cette clé
# (Note: Tu devras peut-être la mettre à jour après l'import Meilisearch)

# --- CONFIGURATION DU VOYAGE TEMPOREL ---
ANNEE_DEBUT = 2000
ANNEE_FIN = 2025
PAGES_PAR_ANNEE = 120  # ~3120 pages au total

# --- INITIALISATION API ---
wiki = wikipediaapi.Wikipedia(
    user_agent='NeoSeekBot/2.0 (SRAS Historical Mode)',
    language='fr'
)

documents = []
visited_global = set() # Pour ne pas réindexer la même chose

print(f"🤖 Démarrage de NeoSeek - Mode HISTOIRE ({ANNEE_DEBUT}-{ANNEE_FIN})")
print(f"📚 Objectif : ~{PAGES_PAR_ANNEE} pages par année.")

# --- BOUCLE PRINCIPALE (D'ANNÉE EN ANNÉE) ---
for annee in range(ANNEE_DEBUT, ANNEE_FIN + 1):
    page_titre_racine = str(annee)
    print(f"\n📅 TRAITEMENT DE L'ANNÉE : {page_titre_racine} ...")
    
    try:
        # 1. On récupère la page principale de l'année
        page_racine = wiki.page(page_titre_racine)
        
        if not page_racine.exists():
            print(f"⚠️ Page {page_titre_racine} introuvable.")
            continue

        # Liste locale pour cette année
        to_visit = [page_racine.title] 
        # On ajoute les liens trouvés sur la page de l'année pour les explorer
        for link_title, link_obj in page_racine.links.items():
            if link_obj.namespace == wikipediaapi.Namespace.MAIN:
                to_visit.append(link_title)

        count_annee = 0
        
        # 2. On explore les liens de cette année jusqu'à atteindre la limite (120)
        while to_visit and count_annee < PAGES_PAR_ANNEE:
            titre = to_visit.pop(0)

            if titre in visited_global:
                continue

            # On évite les pages qui sont juste des dates (ex: "12 mars")
            if re.match(r'^\d{1,2} [a-z]+', titre) or (re.match(r'^\d{4}$', titre) and titre != str(annee)):
                continue

            try:
                page = wiki.page(titre)
                if not page.exists(): continue
                
                # Si le résumé est trop court, on zappe
                if len(page.summary) < 100: continue
                
                # ----------------------------------------------------
                # CALCUL DU SCORE D'AUTORITÉ AUTO-RÉFÉRENTIEL (SRAS)
                link_count = len(page.links) # Plus il y a de liens, plus la page est un carrefour fiable
                # ----------------------------------------------------
                
                # Création du document
                doc = {
                    "id": len(visited_global) + 1 + annee * 10000, # ID unique
                    "url": page.fullurl,
                    "title": page.title,
                    "content": page.summary,
                    "internal_link_count": link_count # NOUVEAU CHAMP DE SCORE SRAS
                }
                
                documents.append(doc)
                visited_global.add(titre)
                count_annee += 1
                
                print(f"   ✅ [{count_annee}/{PAGES_PAR_ANNEE}] Score SRAS: {link_count} - Indexé : {doc['title']}")
                
                # Envoi par paquets
                if len(documents) >= 10:
                    requests.post(
                        f"{MEILI_URL}/indexes/docs/documents",
                        headers={"Authorization": f"Bearer {MEILI_KEY}"},
                        json=documents
                    )
                    documents = [] 
                
                time.sleep(0.1)

            except Exception as e:
                # print(f"   ❌ Erreur sur {titre}: {e}")
                continue

    except Exception as e:
        print(f"⚠️ Erreur critique sur l'année {annee} : {e}")

# Envoi du dernier paquet
if documents:
    requests.post(
        f"{MEILI_URL}/indexes/docs/documents",
        headers={"Authorization": f"Bearer {MEILI_KEY}"},
        json=documents
    )

print("\n🎉 MISSION ACCOMPLIE ! L'HISTOIRE EST MAINTENANT DOTÉE D'UN SCORE DE CONFIANCE.")