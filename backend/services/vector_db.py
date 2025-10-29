import chromadb
from chromadb.config import Settings
import os

def init_chroma():
    """
    Initialise ChromaDB avec persistance correcte
    """
    from config import CHROMA_DIR, COLLECTION_NAME
    
    # Créer le dossier s'il n'existe pas
    os.makedirs(CHROMA_DIR, exist_ok=True)
    
    # Utiliser PersistentClient pour garantir la persistance
    client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    # Récupérer ou créer la collection
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' chargée ({collection.count()} documents)")
    except:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # Utiliser la distance cosinus
        )
        print(f"✅ Collection '{COLLECTION_NAME}' créée")
    
    return client, collection


def reset_chroma():
    """
    Réinitialise complètement ChromaDB (supprime toutes les données)
    """
    from config import CHROMA_DIR, COLLECTION_NAME
    
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' supprimée")
    except:
        print(f"⚠️  Collection '{COLLECTION_NAME}' n'existait pas")
    
    # Recréer la collection
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"✅ Collection '{COLLECTION_NAME}' recréée")
    
    return client, collection