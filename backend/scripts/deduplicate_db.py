import requests
import json
import time

# --- CONFIGURATION ---
MEILI_URL = "http://127.0.0.1:7700"
MEILI_KEY = "rVR_Z3zs5Ah3zwbrhj1HL7SgxoCssmdBiQd6A1Coj4" # MASTER KEY requise pour la suppression
INDEX_UID = "docs"
BATCH_SIZE = 1000 # Nombre de documents à récupérer à la fois

def fetch_all_documents():
    """Récupère tous les documents de l'index par pagination."""
    print("1. Récupération de tous les documents...")
    all_documents = []
    offset = 0
    
    while True:
        try:
            response = requests.get(
                f"{MEILI_URL}/indexes/{INDEX_UID}/documents",
                headers={"Authorization": f"Bearer {MEILI_KEY}"},
                params={"limit": BATCH_SIZE, "offset": offset, "fields": "id,url"}
            )
            response.raise_for_status() # Lève une exception si le statut est une erreur (4xx ou 5xx)
            
            data = response.json()
            documents = data.get('results', [])
            all_documents.extend(documents)
            
            if not documents or len(documents) < BATCH_SIZE:
                break
                
            offset += BATCH_SIZE
            print(f"   -> Récupéré {len(all_documents)} documents...")
            
        except requests.exceptions.RequestException as e:
            print(f"ERREUR lors de la récupération des documents : {e}")
            return None
    
    print(f"-> Récupération totale terminée : {len(all_documents)} documents.")
    return all_documents

def find_duplicates(documents):
    """Identifie les documents doublons basés sur l'URL, en conservant une instance."""
    print("2. Identification des doublons par URL...")
    
    # Structure pour stocker l'URL en clé et la liste des IDs correspondants
    url_to_ids = {}
    
    for doc in documents:
        url = doc.get('url')
        doc_id = doc.get('id')
        
        if url and doc_id:
            if url not in url_to_ids:
                url_to_ids[url] = []
            url_to_ids[url].append(doc_id)
            
    duplicates_to_delete = []
    
    for url, ids in url_to_ids.items():
        if len(ids) > 1:
            # Conserver la première ID et marquer les autres comme doublons à supprimer
            duplicates_to_delete.extend(ids[1:])
            
    return duplicates_to_delete

def delete_documents(ids_to_delete):
    """Supprime les IDs spécifiés de l'index Meilisearch."""
    if not ids_to_delete:
        print("4. Aucune ID à supprimer. Fin de l'opération.")
        return

    print(f"3. Suppression de {len(ids_to_delete)} doublons...")
    
    try:
        # L'API Meilisearch permet de supprimer une liste d'IDs en une seule requête POST
        response = requests.post(
            f"{MEILI_URL}/indexes/{INDEX_UID}/documents/delete-batch",
            headers={
                "Authorization": f"Bearer {MEILI_KEY}",
                "Content-Type": "application/json"
            },
            json=ids_to_delete
        )
        response.raise_for_status()
        
        task_info = response.json()
        print(f"-> Tâche de suppression lancée. ID de tâche : {task_info.get('taskUid')}")
        print("   Vérifiez l'état de la tâche dans la console Meilisearch.")

    except requests.exceptions.RequestException as e:
        print(f"ERREUR lors de la suppression des documents : {e}")

if __name__ == '__main__':
    start_time = time.time()
    
    documents = fetch_all_documents()
    
    if documents is not None:
        ids_to_delete = find_duplicates(documents)
        delete_documents(ids_to_delete)
        
    end_time = time.time()
    print(f"\nOpération de déduplication terminée en {end_time - start_time:.2f} secondes.")