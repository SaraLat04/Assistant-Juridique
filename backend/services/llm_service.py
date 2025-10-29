import requests
from config import HF_TOKEN

# =======================
# 💬 Fonctions principales
# =======================
def ask_general(question: str) -> str:
    """
    Génère une réponse générale (non juridique) avec l'IA.
    """
    print("\n🌐 Mode assistant général activé")
    
    # Essayer les modèles IA dans l'ordre
    ai_response = try_ai_models_general(question)
    
    if ai_response:
        return f"💬 **Réponse :**\n\n{ai_response.strip()}"
    
    # Fallback si aucun modèle ne répond
    return """💬 **Réponse :**

Bonjour ! Je suis un assistant conversationnel.

Malheureusement, je ne peux pas répondre à votre question pour le moment car les services d'IA sont temporairement indisponibles.

💡 **Je peux vous aider avec :**
- Questions sur le droit marocain (codes pénal, civil, travail, etc.)
- Explications juridiques
- Interprétation d'articles de loi

N'hésitez pas à me poser une question juridique ! ⚖️"""


def try_ai_models_general(question: str) -> str:
    """Essaie les modèles IA pour une question générale (sans contexte juridique)"""
    
    # 1️⃣ OpenAI
    print("\n🔄 Tentative 1/3 : OpenAI...")
    try:
        response = try_openai_general(question)
        if response:
            print("✅ OpenAI a répondu")
            return response
    except Exception as e:
        print(f"❌ OpenAI : {str(e)[:80]}")
    
    # 2️⃣ Groq
    print("\n🔄 Tentative 2/3 : Groq...")
    try:
        response = try_groq_general(question)
        if response:
            print("✅ Groq a répondu")
            return response
    except Exception as e:
        print(f"❌ Groq : {str(e)[:80]}")
    
    # 3️⃣ HuggingFace
    print("\n🔄 Tentative 3/3 : HuggingFace...")
    try:
        response = try_huggingface_general(question)
        if response:
            print("✅ HuggingFace a répondu")
            return response
    except Exception as e:
        print(f"❌ HuggingFace : {str(e)[:80]}")
    
    return None


def try_openai_general(question: str) -> str:
    try:
        from config import OPENAI_API_KEY
        from openai import OpenAI
        
        if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-votre-clé-ici":
            return None
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant conversationnel utile et amical. Réponds en français de manière claire et concise."},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except:
        return None


def try_groq_general(question: str) -> str:
    try:
        from config import GROQ_API_KEY
        from groq import Groq
        
        if not GROQ_API_KEY or GROQ_API_KEY == "sk-votre-clé-ici":
            return None
        
        client = Groq(api_key=GROQ_API_KEY)
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un assistant conversationnel utile et amical. Réponds en français de manière claire et concise."},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return completion.choices[0].message.content.strip()
    except:
        return None


def try_huggingface_general(question: str) -> str:
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    models = [
        "mistralai/Mistral-7B-Instruct-v0.2",
        "meta-llama/Llama-2-7b-chat-hf"
    ]
    
    prompt = f"<s>[INST] {question} [/INST]"
    
    for model_id in models:
        try:
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_id}",
                headers=headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 250,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0 and 'generated_text' in data[0]:
                    text = data[0]['generated_text'].strip()
                    if text and len(text) > 30:
                        return text
        except:
            continue
    
    return None


def ask_juridique(question: str, context: str) -> str:
    """
    Génère une réponse juridique basée sur le contexte.
    """
    if not context or not context.strip():
        return "❌ Aucun article pertinent n'a été trouvé dans la base de données juridique."

    # Essayer les modèles IA (OpenAI, Groq, HuggingFace)
    ai_response = try_ai_models(question, context)

    if ai_response:
        return format_ai_response_with_sources(ai_response, context)

    # Si aucun modèle n'a répondu → fallback structuré
    print("⚠️ Tous les modèles IA ont échoué → Utilisation du fallback")
    return generate_smart_fallback(question, context)


# =======================
# 🔁 Gestion des modèles IA
# =======================
def try_ai_models(question: str, context: str) -> str:
    """Essaie différents modèles IA dans l'ordre"""
    
    # 1️⃣ OpenAI
    print("\n🔄 Tentative 1/3 : OpenAI (GPT-3.5-turbo)...")
    try:
        openai_response = try_openai(question, context)
        if openai_response:
            print("✅ OpenAI a répondu avec succès")
            return openai_response
        else:
            print("❌ OpenAI : Clé API invalide ou non configurée")
    except Exception as e:
        print(f"❌ OpenAI : Erreur - {str(e)[:100]}")

    # 2️⃣ Groq
    print("\n🔄 Tentative 2/3 : Groq (Llama-3.1-8b)...")
    try:
        groq_response = try_groq(question, context)
        if groq_response:
            print("✅ Groq a répondu avec succès")
            return groq_response
        else:
            print("❌ Groq : Clé API invalide ou non configurée")
    except Exception as e:
        print(f"❌ Groq : Erreur - {str(e)[:100]}")

    # 3️⃣ HuggingFace
    print("\n🔄 Tentative 3/3 : HuggingFace (Mistral/Llama)...")
    try:
        hf_response = try_huggingface(question, context)
        if hf_response:
            print("✅ HuggingFace a répondu avec succès")
            return hf_response
        else:
            print("❌ HuggingFace : Aucune réponse valide obtenue")
    except Exception as e:
        print(f"❌ HuggingFace : Erreur - {str(e)[:100]}")

    print("\n❌ Aucun modèle IA n'a pu générer de réponse")
    return None


# =======================
# 🧠 OpenAI
# =======================
def try_openai(question: str, context: str) -> str:
    try:
        from config import OPENAI_API_KEY
        from openai import OpenAI

        if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-votre-clé-ici":
            print("   ⏭️  Clé OpenAI non configurée (placeholder détecté)")
            return None

        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""Tu es un assistant juridique marocain expert, capable d'expliquer clairement les lois et leurs implications.

Contexte :
{context}

Question :
{question}

Réponds en français clair et naturel comme un avocat qui conseille un client :
- Donne une explication simple et structurée (150 à 250 mots)
- Mentionne les principes généraux du droit marocain
- Ne cite pas encore les articles (ils seront ajoutés après)
- Termine par une phrase de conseil pratique

Réponse :
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant juridique marocain expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"   ⚠️  Erreur OpenAI : {str(e)[:80]}")
        return None


# =======================
# ⚡ Groq
# =======================
def try_groq(question: str, context: str) -> str:
    try:
        from config import GROQ_API_KEY
        from groq import Groq

        if not GROQ_API_KEY or GROQ_API_KEY == "sk-votre-clé-ici":
            print("   ⏭️  Clé Groq non configurée (placeholder détecté)")
            return None

        print(f"   🔑 Clé Groq détectée : {GROQ_API_KEY[:20]}...")
        client = Groq(api_key=GROQ_API_KEY)

        prompt = f"""Tu es un assistant juridique marocain expert, capable d'expliquer clairement les lois et leurs implications.

Contexte :
{context}

Question :
{question}

Réponds en français clair et naturel comme un avocat qui conseille un client :
- Donne une explication simple et structurée (150 à 250 mots)
- Mentionne les principes généraux du droit marocain
- Ne cite pas encore les articles (ils seront ajoutés après)
- Termine par une phrase de conseil pratique
"""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un assistant juridique marocain expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )

        result = completion.choices[0].message.content.strip()
        print(f"   📝 Réponse Groq reçue : {len(result)} caractères")
        return result
    except Exception as e:
        print(f"   ⚠️  Erreur Groq : {str(e)[:80]}")
        return None


# =======================
# 🤖 HuggingFace
# =======================
def try_huggingface(question: str, context: str) -> str:
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    models = [
        "mistralai/Mistral-7B-Instruct-v0.2",
        "meta-llama/Llama-2-7b-chat-hf"
    ]

    prompt = f"""<s>[INST] Tu es un assistant juridique marocain expert. Réponds de manière claire, naturelle et structurée.

Contexte :
{context}

Question :
{question}

Réponds en français clair et professionnel, comme un avocat qui conseille un client. Ne cite pas encore les articles (ils seront ajoutés après). [/INST]
"""

    for i, model_id in enumerate(models, 1):
        try:
            print(f"   🤖 Test modèle {i}/{len(models)} : {model_id.split('/')[-1]}")
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_id}",
                headers=headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 300,
                        "temperature": 0.7,
                        "return_full_text": False,
                        "do_sample": True
                    }
                },
                timeout=25
            )

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0 and 'generated_text' in data[0]:
                    text = data[0]['generated_text'].strip()
                    if text and len(text) > 50:
                        print(f"   ✅ Modèle {model_id.split('/')[-1]} a répondu : {len(text)} caractères")
                        return text
                    else:
                        print(f"   ⚠️  Réponse trop courte ({len(text)} caractères)")
                else:
                    print(f"   ⚠️  Format de réponse invalide")
            elif response.status_code == 503:
                print(f"   ⏳ Modèle en cours de chargement (503)")
            else:
                print(f"   ❌ Erreur HTTP {response.status_code}")
        except Exception as e:
            print(f"   ⚠️  Erreur : {str(e)[:60]}")
            continue

    return None


# =======================
# 🧾 Mise en forme finale
# =======================
def format_ai_response_with_sources(ai_response: str, context: str) -> str:
    """
    Formate la réponse IA comme ChatGPT + ajoute les articles à la fin
    """
    # Extraire les articles du contexte
    articles = []
    for line in context.split('\n\n'):
        line = line.strip()
        if line and len(line) > 20:
            articles.append(line)

    formatted = f"""💬 **Réponse juridique :**

{ai_response.strip()}

---

📚 **Références légales :**
"""

    # Ajouter jusqu'à 3 articles
    for i, article in enumerate(articles[:3], 1):
        lines = article.split('\n')
        if len(lines) >= 2:
            reference = lines[0].strip()
            content = ' '.join(lines[1:]).strip()
            if len(content) > 250:
                content = content[:250] + "..."
            formatted += f"\n**{i}. {reference}**\n> {content}\n"

    formatted += "\n---\n_💼 Source : Base de données juridique marocaine_"
    return formatted


# =======================
# 🧩 Fallback sans IA
# =======================
def generate_smart_fallback(question: str, context: str) -> str:
    articles = []
    for line in context.split('\n\n'):
        line = line.strip()
        if line and len(line) > 20:
            articles.append(line)

    intro = f"💬 **Réponse juridique :**\n\n"
    intro += f"D'après la législation marocaine, concernant votre question sur **{question}**, voici les dispositions pertinentes :\n\n"

    for i, article in enumerate(articles[:3], 1):
        lines = article.split('\n')
        if len(lines) >= 2:
            reference = lines[0].strip()
            content = ' '.join(lines[1:]).strip()
            if len(content) > 250:
                content = content[:250] + "..."
            intro += f"**{i}. {reference}**\n> {content}\n\n"

    intro += "---\n📌 **Remarque :** Cette réponse est basée sur les textes juridiques marocains en vigueur. Pour une interprétation détaillée de votre situation, il est conseillé de consulter un avocat.\n\n_💼 Source : Base de données juridique marocaine_"
    return intro