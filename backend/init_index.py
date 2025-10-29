import pandas as pd
import os
from services.vector_db import init_chroma

def load_csv(file_name):
    """Charge un fichier CSV"""
    if os.path.exists(file_name):
        df = pd.read_csv(file_name, encoding='utf-8-sig')
        return df
    else:
        raise FileNotFoundError(f"{file_name} introuvable.")

def preprocess_df(df):
    """Prétraite le DataFrame"""
    # Nettoyer les noms de colonnes
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Mapping des colonnes
    col_mapping = {
        'doc': 'DOC',
        'titre': 'Titre',
        'chapitre': 'Chapitre',
        'section': 'Section',
        'article': 'Article',
        'contenu': 'Contenu',
        'texte': 'Contenu',
        'pages': 'Pages'
    }
    
    df = df.rename(columns={col: col_mapping.get(col, col) for col in df.columns})
    
    # Ajouter les colonnes manquantes
    for col in ['DOC', 'Titre', 'Chapitre', 'Section', 'Article', 'Contenu', 'Pages']:
        if col not in df.columns:
            df[col] = ''
    
    # Créer le texte complet
    df['texte_complet'] = (
        df['Article'].fillna('').astype(str) + ' ' + 
        df['Contenu'].fillna('').astype(str)
    )
    df['texte_complet'] = df['texte_complet'].str.replace('\r\n', ' ').str.strip()
    
    return df

def prepare_chunks(df, source_file):
    """Prépare les chunks pour l'indexation"""
    texts = []
    metadatas = []
    ids = []
    
    for idx, row in df.iterrows():
        text = str(row.get('texte_complet', '')).strip()
        
        # Ignorer les textes vides ou trop courts
        if not text or len(text) < 10:
            continue
        
        texts.append(text)
        
        # Métadonnées
        metadatas.append({
            'DOC': str(row.get('DOC', '')),
            'Titre': str(row.get('Titre', '')),
            'Chapitre': str(row.get('Chapitre', '')),
            'Section': str(row.get('Section', '')),
            'Article': str(row.get('Article', '')),
            'Pages': str(row.get('Pages', '')),
            'source': source_file
        })
        
        # ID unique
        file_name = os.path.basename(source_file).replace('.csv', '')
        ids.append(f"{file_name}_{idx}_{hash(text) % 1000000}")
    
    return texts, metadatas, ids

def index_texts(texts, metadatas, ids):
    """Indexe les textes dans ChromaDB"""
    if len(texts) == 0:
        print("❌ Aucun texte à indexer")
        return
    
    client, collection = init_chroma()
    
    print(f"\n📊 Documents existants : {collection.count()}")
    
    # Indexer par batch pour éviter les erreurs de mémoire
    batch_size = 100
    total_indexed = 0
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        
        try:
            collection.add(
                documents=batch_texts,
                metadatas=batch_metas,
                ids=batch_ids
            )
            total_indexed += len(batch_texts)
            print(f"✅ Indexé {total_indexed}/{len(texts)} documents")
        except Exception as e:
            print(f"⚠️  Erreur batch {i}-{i+batch_size}: {e}")
            continue
    
    print(f"\n🎉 Total dans ChromaDB : {collection.count()} documents")

# ==================== SCRIPT PRINCIPAL ====================

if __name__ == "__main__":
    print("🚀 Début de l'indexation...\n")
    
    csv_files = [
        "data/loi_articles.csv",
        "data/IGOC_2024_articles_corrigee2.csv",
        "data/Code_General_Des_Impots_Articles.csv"
    ]
    
    all_texts, all_metadatas, all_ids = [], [], []
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"⚠️  Fichier introuvable : {csv_file}")
            continue
        
        print(f"📂 Traitement de {csv_file}...")
        
        try:
            # Charger et prétraiter
            df = load_csv(csv_file)
            df = preprocess_df(df)
            
            print(f"   📄 Lignes : {len(df)}")
            print(f"   📋 Colonnes : {list(df.columns)}")
            
            # Préparer les chunks
            texts, metadatas, ids = prepare_chunks(df, csv_file)
            
            print(f"   ✅ Chunks créés : {len(texts)}")
            
            if len(texts) > 0:
                print(f"   📝 Exemple : {texts[0][:100]}...")
            
            all_texts.extend(texts)
            all_metadatas.extend(metadatas)
            all_ids.extend(ids)
            
        except Exception as e:
            print(f"   ❌ Erreur : {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Indexation finale
    if all_texts:
        print(f"\n{'='*60}")
        print(f"📊 Total à indexer : {len(all_texts)} documents")
        print(f"{'='*60}\n")
        index_texts(all_texts, all_metadatas, all_ids)
        print("\n✅ Indexation terminée !")
    else:
        print("\n❌ Aucune donnée à indexer ! Vérifiez vos fichiers CSV.")