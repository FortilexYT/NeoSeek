import requests
import json

# --- CONFIGURATION ---
MEILI_URL = "http://127.0.0.1:7700"
MEILI_KEY = "rVR_Z3zs5Ah3zwbrhj1HL7SgxoCssmdBiQd6A1Coj4" # Vérifie ta clé

# Dictionnaire de synonymes généré par l'IA (43 thèmes -> milliers de paires)
SYNONYMS_FROM_AI = {
    "Intelligence Artificielle": ["IA", "systèmes intelligents", "apprentissage automatique", "agents intelligents", "technologies cognitives", "algorithmes adaptatifs", "modèles prédictifs"],
    "Exploration Spatiale": ["missions spatiales", "astronautique", "voyages interplanétaires", "programmes spatiaux", "colonisation spatiale", "technologies orbitales", "expéditions interstellaires"],
    "Physique Quantique": ["mécanique quantique", "théorie des quanta", "ondes de probabilité", "superposition quantique", "intrication quantique", "physique des particules", "champ quantique"],
    "Langage Python": ["programmation Python", "scripts Python", "développement Python", "frameworks Python", "bibliothèques Python", "syntaxe Python", "outils Python"],
    "Blockchain et Crypto": ["technologie blockchain", "cryptomonnaies", "registre distribué", "crypto-actifs", "transactions décentralisées", "minage", "smart contracts"],
    "Cybersécurité": ["sécurité informatique", "protection des systèmes", "sécurité réseau", "sécurité des données", "cryptographie", "sécurité offensive", "sécurité défensive"],
    "Histoire d'Internet": ["origines du web", "ARPANET", "évolution du réseau", "protocoles fondateurs", "développement du WWW", "réseaux pionniers", "infrastructure Internet"],
    "Réalité Virtuelle": ["VR", "mondes immersifs", "simulation virtuelle", "technologies immersives", "interfaces 3D", "expériences immersives", "casques VR"],
    "Voitures autonomes": ["véhicules autonomes", "ADAS", "LiDAR", "cartographie HD", "intelligence embarquée", "algorithmes de conduite", "mobilité autonome"],
    "Énergie nucléaire": ["fission nucléaire", "fusion nucléaire", "centrales nucléaires", "réacteurs nucléaires", "radioactivité", "sûreté nucléaire", "production énergétique"],
    "Histoire de France": ["chronologie française", "événements historiques", "monarchie française", "révolutions françaises", "guerres françaises", "dynasties françaises", "patrimoine historique"],
    "Empire Romain": ["Rome antique", "civilisation romaine", "armée romaine", "droit romain", "architecture romaine", "empereurs romains", "expansion romaine"],
    "Seconde Guerre Mondiale": ["WWII", "forces alliées", "axe", "fronts militaires", "Shoah", "batailles majeures", "résistance"],
    "Révolution Industrielle": ["industrialisation", "mécanisation", "usines", "progrès techniques", "urbanisation", "machines à vapeur", "production de masse"],
    "Merveilles du monde": ["sites antiques", "monuments historiques", "patrimoine mondial", "architecture antique", "merveilles architecturales", "sites emblématiques", "trésors archéologiques"],
    "Géographie du Japon": ["relief japonais", "climat japonais", "archipel nippon", "volcans japonais", "rivières japonaises", "villes japonaises", "régions japonaises"],
    "Changement climatique": ["réchauffement climatique", "gaz à effet de serre", "fonte des glaciers", "montée des eaux", "biodiversité menacée", "énergies renouvelables", "événements climatiques extrêmes"],
    "Océanographie": ["sciences marines", "biologie marine", "courants océaniques", "écosystèmes marins", "fonds marins", "exploration océanique", "pollution marine"],
    "Cinéma des années 90": ["films cultes 90s", "cinéma indépendant", "blockbusters 90s", "réalisateurs emblématiques", "effets spéciaux numériques", "séries TV 90s", "genres cinématographiques"],
    "Musique Classique": ["symphonies", "opéra", "baroque", "romantisme musical", "orchestre", "musique de chambre", "solfège"],
    "Peinture Impressionniste": ["impressionnisme", "Van Gogh", "Monet", "post-impressionnisme", "lumière et couleur", "musée d'Orsay", "paysages impressionnistes"],
    "Mythologie Grecque": ["dieux olympiens", "héros mythologiques", "créatures mythiques", "l'Olympe", "les Enfers", "légendes grecques", "Titans"],
    "Littérature française": ["Victor Hugo", "Molière", "romantisme", "surréalisme", "poésie française", "théâtre classique", "existentialisme"],
    "Philosophie antique": ["Platon", "Aristote", "Socrate", "stoïcisme", "présocratiques", "philosophie hellénistique", "démocratie athénienne"],
    "Architecture moderne": ["Bauhaus", "Le Corbusier", "style international", "urbanisme", "gratte-ciel", "architecture durable", "design contemporain"],
    "Recette Pâte à crêpes": ["crêpes bretonnes", "pâte sans grumeaux", "farine de blé noir", "beurre clarifié", "crêpière", "fermentation de pâte", "garnitures traditionnelles"],
    "Recette Pizza maison": ["pâte à pizza", "levain", "sauce tomate maison", "cuisson au four à bois", "style napolitain", "garnitures originales", "techniques de pétrissage"],
    "Jardinage débutant": ["semis", "compostage", "plantes d'intérieur", "potager", "outils de jardinage", "irrigation", "calendrier lunaire"],
    "Premiers secours": ["RCP", "PLS", "défibrillateur", "hémorragie", "brûlures", "alerte 112", "soins d'urgence"],
    "Exercices de musculation": ["HIIT", "gainage", "programme de force", "squat", "échauffement", "suppléments protéinés", "anatomie musculaire"],
    "Nutrition saine": ["régime végétalien", "protéines", "vitamines", "microbiote intestinal", "alimentation équilibrée", "hydratation", "cuisine saine"],
    "Sommeil réparateur": ["cycle du sommeil", "REM", "insomnie", "apnée du sommeil", "hygiène du sommeil", "rythmes circadiens", "rêves lucides"],
    "Dinosaures": ["Tyrannosaurus Rex", "Jurassique", "fossiles", "paléontologie", "extinction des dinosaures", "reptiles volants", "dinosaures à plumes"],
    "Félins sauvages": ["tigres", "lions", "léopards", "guépards", "panthères", "pumas", "conservation des espèces"],
    "Forêt amazonienne": ["déforestation", "biodiversité", "fleuve Amazone", "tribus indigènes", "espèces menacées", "plantes médicinales", "climat équatorial"],
    "Système solaire": ["planètes", "orbites", "astéroïdes", "comètes", "gravité", "galaxies", "exploration spatiale"],
    "Recyclage plastique": ["tri des déchets", "plastique biodégradable", "économie circulaire", "pollution plastique", "centres de tri", "empreinte carbone", "compostage industriel"]
}

try:
    print("🧠 Envoi du dictionnaire de synonymes IA à NeoSeek...")
    # PUT envoie les données de remplacement
    requests.put(
        f"{MEILI_URL}/indexes/docs/settings/synonyms",
        headers={"Authorization": f"Bearer {MEILI_KEY}", "Content-Type": "application/json"},
        json=SYNONYMS_FROM_AI
    )
    print("✅ Synonymes de l'IA installés avec succès !")
    print("👉 Maintenant, si tu cherches 'Astuce code' ou 'PC', NeoSeek te comprend.")

except Exception as e:
    print(f"❌ Erreur : {e}")