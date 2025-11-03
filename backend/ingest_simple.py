"""
Script d'ingestion CSV simplifié
ChromaDB génère les embeddings automatiquement
"""

import os
import pandas as pd
import uuid
import re
from services.vector_db import init_chroma, reset_chroma

# =======================
# 📂 Fonctions de chargement
# =======================

def load_csv(file_name):
    """Charge un fichier CSV"""
    if os.path.exists(file_name):
        df = pd.read_csv(file_name, encoding='utf-8')
        print(f"✅ Fichier chargé : {file_name} ({len(df)} lignes)")
        return df
    else:
        raise FileNotFoundError(f"❌ {file_name} introuvable !")


def preprocess_csv(df, file_name):
    """Prétraite le DataFrame pour standardiser les colonnes"""
    # Nettoyer les noms de colonnes
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Mapper les colonnes vers un format standard
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
    df['texte_complet'] = df['Article'].fillna('') + ' ' + df['Contenu'].fillna('')
    df['texte_complet'] = df['texte_complet'].str.replace('\r\n', ' ').str.strip()
    
    print(f"✅ Prétraitement terminé : {len(df)} entrées")
    return df


def chunk_text(text, max_chars=1000):
    """Découpe un texte long en chunks plus petits"""
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, chunk = [], ""
    
    for sent in sents:
        if len(chunk) + len(sent) < max_chars:
            chunk += " " + sent
        else:
            if chunk.strip():
                chunks.append(chunk.strip())
            chunk = sent
    
    if chunk.strip():
        chunks.append(chunk.strip())
    
    return chunks


def prepare_chunks(df, source_name):
    """Prépare les chunks pour l'ingestion dans ChromaDB"""
    texts, metadatas, ids = [], [], []
    
    for idx, row in df.iterrows():
        content = str(row['texte_complet']).strip()
        
        if not content or content == 'nan':
            continue
        
        # Découper si trop long
        chunks = chunk_text(content) if len(content) > 1000 else [content]
        
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({
                'source': source_name,
                'doc': str(row['DOC']),
                'article': str(row['Article']),
                'pages': str(row['Pages']),
                'titre': str(row['Titre']),
                'chunk_id': i
            })
            ids.append(str(uuid.uuid4()))
    
    print(f"✅ {len(texts)} chunks créés depuis {source_name}")
    return texts, metadatas, ids


# =======================
# 🚀 Fonction principale d'ingestion
# =======================

def ingest_csv_files(csv_files: list, reset: bool = False):
    """
    Ingère plusieurs fichiers CSV dans ChromaDB
    ChromaDB génère les embeddings automatiquement
    
    Args:
        csv_files: Liste de chemins vers les fichiers CSV
        reset: Si True, réinitialise la base avant l'ingestion
    """
    print("\n" + "="*60)
    print("🚀 DÉMARRAGE DE L'INGESTION DES DOCUMENTS JURIDIQUES")
    print("="*60 + "\n")
    
    # Initialiser ou réinitialiser ChromaDB
    if reset:
        print("🔄 Réinitialisation de ChromaDB...")
        client, collection = reset_chroma()
    else:
        client, collection = init_chroma()
    
    # Traiter chaque fichier CSV
    all_texts, all_metadatas, all_ids = [], [], []
    
    for csv_file in csv_files:
        print(f"\n📄 Traitement de : {csv_file}")
        print("-" * 60)
        
        try:
            # Charger et prétraiter
            df = load_csv(csv_file)
            df = preprocess_csv(df, csv_file)
            
            # Extraire le nom du fichier comme source
            source_name = os.path.basename(csv_file).replace('.csv', '')
            
            # Préparer les chunks
            texts, metadatas, ids = prepare_chunks(df, source_name)
            
            all_texts.extend(texts)
            all_metadatas.extend(metadatas)
            all_ids.extend(ids)
            
        except Exception as e:
            print(f"❌ Erreur avec {csv_file} : {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Vérifier qu'on a des données
    if not all_texts:
        print("\n❌ Aucun document à ingérer !")
        return
    
    print(f"\n📊 TOTAL : {len(all_texts)} chunks à ingérer")
    
    # Insérer dans ChromaDB par batches
    # ChromaDB va générer les embeddings automatiquement
    print("\n💾 Insertion dans ChromaDB (embeddings auto)...")
    batch_size = 100  # Batch plus petit pour éviter les timeouts
    
    for i in range(0, len(all_texts), batch_size):
        end = min(i + batch_size, len(all_texts))
        
        print(f"   🔄 Batch {i//batch_size + 1} : traitement de {i} à {end}...", end='')
        
        collection.add(
            ids=all_ids[i:end],
            documents=all_texts[i:end],
            metadatas=all_metadatas[i:end]
            # Pas d'embeddings → ChromaDB les génère automatiquement
        )
        
        print(f" ✅")
    
    # Résumé final
    print("\n" + "="*60)
    print("✅ INGESTION TERMINÉE AVEC SUCCÈS !")
    print("="*60)
    print(f"📊 Total documents dans ChromaDB : {collection.count()}")
    print(f"💾 Stockage : {os.path.abspath('chroma_db/')}")
    print("\n💡 Testez maintenant :")
    print("   python test_chroma.py")
    print("   python app.py")


# =======================
# 🎯 Script principal
# =======================

if __name__ == "__main__":
    # 📂 Rechercher automatiquement tous les CSV dans data/
    data_dir = "data"
    
    if os.path.exists(data_dir):
        csv_files = [
            os.path.join(data_dir, f) 
            for f in os.listdir(data_dir) 
            if f.endswith('.csv')
        ]
    else:
        csv_files = []
    
    if not csv_files:
        print("\n❌ AUCUN FICHIER CSV TROUVÉ !")
        print("\n💡 Créez un dossier 'data/' et placez-y vos fichiers CSV")
        print("\nFormat attendu des colonnes :")
        print("   - doc ou DOC : Nom du document (ex: 'Code Pénal')")
        print("   - article ou Article : Numéro de l'article (ex: 'Article 392')")
        print("   - contenu ou Contenu : Texte de l'article")
        print("   - titre ou Titre : Titre du chapitre (optionnel)")
        print("   - pages ou Pages : Numéro de pages (optionnel)")
        print("\nExemple de structure CSV :")
        print("   DOC,Article,Contenu")
        print('   "Code Pénal","Article 392","Est puni de la réclusion..."')
        print(f"\n📁 Créez le dossier : {os.path.abspath(data_dir)}/")
        
        # Créer un exemple de fichier CSV
        print("\n💡 Création d'un fichier CSV d'exemple...")
        os.makedirs(data_dir, exist_ok=True)
        
        example_csv = os.path.join(data_dir, "exemple_test.csv")
        with open(example_csv, 'w', encoding='utf-8') as f:
            f.write('DOC,Article,Contenu\n')
            f.write('"Code Pénal Marocain","Article 392","Est puni de la réclusion de cinq à dix ans, quiconque commet un vol dans les circonstances suivantes : lorsque le vol est commis avec violence ou menace de violence."\n')
            f.write('"Code de la Famille","Article 4","Le mariage est un contrat légal par lequel un homme et une femme s\'unissent en vue d\'une union légale et durable."\n')
            f.write('"Code du Travail","Article 6","Est considéré comme salarié toute personne qui s\'est engagée à exercer son activité professionnelle sous la direction d\'un ou plusieurs employeurs moyennant rémunération."\n')
        
        print(f"✅ Fichier créé : {example_csv}")
        print("\n🔄 Relancez le script pour ingérer ce fichier d'exemple")
        
    else:
        print(f"\n✅ {len(csv_files)} fichier(s) CSV trouvé(s) dans {data_dir}/")
        print("\nFichiers à ingérer :")
        for f in csv_files:
            size = os.path.getsize(f) / 1024  # Taille en Ko
            print(f"   - {f} ({size:.1f} Ko)")
        
        # Demander confirmation
        print("\n" + "="*60)
        reset_input = input("🔄 Réinitialiser ChromaDB avant l'ingestion ? (o/n) : ").strip().lower()
        reset = reset_input == 'o'
        print("="*60)
        
        # Lancer l'ingestion
        try:
            ingest_csv_files(csv_files, reset=reset)
        except Exception as e:
            print(f"\n❌ Erreur : {e}")
            import traceback
            traceback.print_exc()