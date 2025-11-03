from services.vector_db import init_chroma

client, collection = init_chroma()

print(f"📊 Nombre total de documents : {collection.count()}")
print("\n🔍 Exemples de documents :\n")

# Récupérer quelques exemples
results = collection.get(limit=10)

for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas']), 1):
    print(f"\n--- Document {i} ---")
    print(f"Source: {meta.get('doc', meta.get('source', 'Inconnu'))}")
    print(f"Article: {meta.get('article', 'N/A')}")
    print(f"Contenu: {doc[:150]}...")
    print("-" * 50)