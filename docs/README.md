 NeoSeek

NeoSeek est un moteur de recherche open source propulsé par Meilisearch et une interface moderne en React/Next.js.

 🚀 Fonctionnalités
- Recherche rapide et tolérante aux fautes de frappe
- Interface simple et intuitive
- Indexation de données personnalisées (JSON, articles, pages web)
- API REST facile à connecter

 📂 Structure du projet
- backend/ → scripts et configuration du moteur
- data/ → données à indexer
- docs/ → documentation du projet
- frontend/ → interface utilisateur
- docker-compose.yml → déploiement simplifié

 ⚙️ Installation
1. Installer [Meilisearch](https://www.meilisearch.com/docs).
2. Lancer le backend avec `python backend/scripts/index_data.py`.
3. Démarrer le frontend avec `npm run dev` (ou `yarn dev`).
4. Accéder à NeoSeek via `http://localhost:3000`.

## 📜 Licence
Projet sous licence **MIT** – libre d’utilisation et de modification.
