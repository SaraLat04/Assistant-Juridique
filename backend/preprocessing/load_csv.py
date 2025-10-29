import os
import pandas as pd
import uuid
import re

def load_csv(file_name):
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
    else:
        raise FileNotFoundError(f"{file_name} introuvable !")
    return df

def preprocess_csv(df, file_name):
    df.columns = [col.strip().lower() for col in df.columns]
    col_mapping = {
        'doc': 'DOC', 'titre': 'Titre', 'chapitre': 'Chapitre',
        'section': 'Section', 'article': 'Article',
        'contenu': 'Contenu', 'texte': 'Contenu', 'pages': 'Pages'
    }
    df = df.rename(columns={col: col_mapping.get(col, col) for col in df.columns})
    for col in ['DOC', 'Titre', 'Chapitre', 'Section', 'Article', 'Contenu', 'Pages']:
        if col not in df.columns:
            df[col] = ''
    df['texte_complet'] = df['Article'].fillna('') + ' ' + df['Contenu'].fillna('')
    df['texte_complet'] = df['texte_complet'].str.replace('\r\n', ' ').str.strip()
    return df

def chunk_text(text, max_chars=1000):
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
    texts, metadatas, ids = [], [], []
    for idx, row in df.iterrows():
        content = str(row['texte_complet']).strip()
        if not content:
            continue
        chunks = chunk_text(content) if len(content) > 1000 else [content]
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({
                'source': source_name,
                'doc': row['DOC'],
                'article': row['Article'],
                'pages': row['Pages'],
                'titre': row['Titre'],
                'chunk_id': i
            })
            ids.append(str(uuid.uuid4()))
    return texts, metadatas, ids
