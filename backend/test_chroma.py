from services.vector_db import init_chroma

print("🔍 Diagnostic ChromaDB\n")
print("="*60)

client, collection = init_chroma()

# 1. Nombre de documents
count = collection.count()
print(f"\n📊 Nombre total de documents : {count}")

if count == 0:
    print("\n❌ La collection est VIDE !")
    print("💡 Action requise : Exécutez 'python index_data.py'")
else:
    # 2. Afficher quelques documents
    print("\n" + "="*60)
    print("📄 Exemples de documents stockés :")
    print("="*60)
    
    results = collection.get(limit=5)
    
    for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas']), 1):
        print(f"\n{i}. Document ID: {results['ids'][i-1]}")
        print(f"   Article : {meta.get('Article', 'N/A')}")
        print(f"   DOC : {meta.get('DOC', 'N/A')}")
        print(f"   Contenu : {doc[:150]}...")
    
    # 3. Test de recherche - "code pénal"
    print("\n" + "="*60)
    print("🔍 Test 1 : Recherche 'code penal'")
    print("="*60)
    
    search1 = collection.query(
        query_texts=["code penal"],
        n_results=3
    )
    
    if search1['documents'][0]:
        for i, (doc, meta, dist) in enumerate(zip(
            search1['documents'][0], 
            search1['metadatas'][0],
            search1['distances'][0]
        ), 1):
            print(f"\n{i}. Score : {dist:.4f}")
            print(f"   Article : {meta.get('Article', 'N/A')}")
            print(f"   Contenu : {doc[:200]}...")
    else:
        print("❌ Aucun résultat")
    
    # 4. Test de recherche - "article 1"
    print("\n" + "="*60)
    print("🔍 Test 2 : Recherche 'article 1 code penal'")
    print("="*60)
    
    search2 = collection.query(
        query_texts=["article 1 code penal"],
        n_results=3
    )
    
    if search2['documents'][0]:
        for i, (doc, meta, dist) in enumerate(zip(
            search2['documents'][0], 
            search2['metadatas'][0],
            search2['distances'][0]
        ), 1):
            print(f"\n{i}. Score : {dist:.4f}")
            print(f"   Article : {meta.get('Article', 'N/A')}")
            print(f"   DOC : {meta.get('DOC', 'N/A')}")
            print(f"   Contenu : {doc[:200]}...")
    else:
        print("❌ Aucun résultat")
    
    # 5. Test de recherche générique
    print("\n" + "="*60)
    print("🔍 Test 3 : Recherche large 'loi maroc'")
    print("="*60)
    
    search3 = collection.query(
        query_texts=["loi maroc"],
        n_results=5
    )
    
    if search3['documents'][0]:
        print(f"\n✅ Trouvé {len(search3['documents'][0])} résultats")
        for i, meta in enumerate(search3['metadatas'][0][:3], 1):
            print(f"   {i}. {meta.get('DOC', 'N/A')} - {meta.get('Article', 'N/A')}")
    else:
        print("❌ Aucun résultat")

print("\n" + "="*60)
print("✅ Diagnostic terminé")
print("="*60)