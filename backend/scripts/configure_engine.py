import requests
import json

# --- CONFIGURATION ---
MEILI_URL = "http://127.0.0.1:7700"
MEILI_KEY = "rVR_Z3zs5Ah3zwbrJhj1HL7SgxoCssmdBiQd6A1Coj4"

print("🧠 Configuration du Cerveau de NeoSeek en cours...")

# 1. Les "Stop Words" (Mots à ignorer car trop courants)
stop_words = [
    "le", "la", "les", "de", "des", "du", "un", "une", "et", "ou", "à", "en", "pour", 
    "par", "sur", "dans", "est", "sont", "c'est", "ce", "ces", "mais", "pas", "plus"
]

# 2. L'ordre d'importance (Ranking)
searchable_attributes = [
    "title",
    "content",
    "url"
]

# 3. Les attributs qui peuvent être utilisés pour le tri (SRAS)
# NOUVEAU : On rend le champ SRAS utilisable par la règle de tri
sortable_attributes = [
    "internal_link_count" 
]

# 4. Les règles de tri
ranking_rules = [
    "sort",       # 👈 NOUVEAU: Mouvement de 'sort' en tête pour prioriser le SRAS !
    "words",      # Le nombre de mots correspondants (Le plus important)
    "typo",       # La tolérance aux fautes d'orthographe
    "proximity",  # Si les mots sont proches les uns des autres
    "attribute",  # L'importance du champ (Titre > Contenu)
    "exactness"
]

settings = {
    "stopWords": stop_words,
    "searchableAttributes": searchable_attributes,
    "rankingRules": ranking_rules,
    "sortableAttributes": sortable_attributes # 👈 Ajout du SRAS aux attributs triables
}

try:
    # Envoi de la configuration
    response = requests.patch(
        f"{MEILI_URL}/indexes/docs/settings",
        headers={
            "Authorization": f"Bearer {MEILI_KEY}",
            "Content-Type": "application/json"
        },
        json=settings
    )

    if response.status_code == 202:
        print("✅ Configuration envoyée avec succès !")
        print("⚙️ Meilisearch est en train de réorganiser toute la base de données...")
        print("⏳ Attends quelques secondes que la tâche finisse.")
    else:
        print(f"❌ Erreur : {response.status_code} - {response.text}")

except Exception as e:
    print(f"❌ Erreur de connexion : {e}")