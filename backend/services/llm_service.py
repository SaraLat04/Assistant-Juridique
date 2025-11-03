import requests
import json

# =======================
# 🏠 Configuration LLM Local
# =======================
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"  # ✅ Llama 3.2

# =======================
# 💬 Fonctions principales
# =======================
def ask_general(question: str) -> str:
    """
    Génère une réponse générale (non juridique) avec Llama 3.2 local.
    """
    print("\n🌐 Mode assistant général activé (Llama 3.2)")
    
    ai_response = call_ollama_general(question)
    
    if ai_response:
        return f"💬 **Réponse :**\n\n{ai_response.strip()}"
    
    return """💬 **Réponse :**

Bonjour ! Je suis un assistant conversationnel.

⚠️ Le modèle local n'est pas disponible. Assurez-vous qu'Ollama est démarré.

💡 **Pour démarrer Ollama :**
```bash
ollama serve
```

💡 **Je peux vous aider avec :**
- Questions sur le droit marocain
- Explications juridiques
- Interprétation d'articles de loi

N'hésitez pas à me poser une question juridique ! ⚖️"""


def ask_juridique(question: str, context: str) -> str:
    """
    Génère une réponse juridique basée sur le contexte avec Llama 3.2 local.
    """
    if not context or not context.strip():
        return "❌ Aucun article pertinent n'a été trouvé dans la base de données juridique."

    print("\n⚖️ Mode juridique activé (Llama 3.2)")
    
    ai_response = call_ollama_juridique(question, context)

    if ai_response:
        return format_ai_response_with_sources(ai_response, context)

    print("⚠️ LLM local n'a pas répondu → Utilisation du fallback")
    return generate_smart_fallback(question, context)


# =======================
# 🦙 Ollama - Appels API
# =======================
def call_ollama_general(question: str) -> str:
    """
    Appelle Ollama (Llama 3.2) localement pour une question générale.
    """
    try:
        print(f"🔄 Appel à Ollama (modèle: {OLLAMA_MODEL})...")
        
        prompt = f"""Tu es un assistant conversationnel utile et amical. 
Réponds en français de manière claire et concise.

Question : {question}

Réponse :"""

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300,
                    "top_p": 0.9
                }
            },
            timeout=180
        )

        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "").strip()
            print(f"✅ Réponse reçue ({len(answer)} caractères)")
            return answer
        else:
            print(f"❌ Erreur Ollama : Status {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("❌ Timeout Ollama (180s dépassé)")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Ollama n'est pas démarré. Lancez : ollama serve")
        return None
    except Exception as e:
        print(f"❌ Erreur Ollama : {str(e)[:100]}")
        return None


def call_ollama_juridique(question: str, context: str) -> str:
    """
    Appelle Ollama (Llama 3.2) localement pour une question juridique.
    """
    try:
        print(f"🔄 Appel juridique à Ollama (modèle: {OLLAMA_MODEL})...")
        
        # Prompt plus structuré et explicite
        prompt = f"""Tu es un assistant juridique expert en droit marocain. Tu dois expliquer les lois de manière claire et accessible.

CONTEXTE JURIDIQUE :
{context}

QUESTION DE L'UTILISATEUR :
{question}

INSTRUCTIONS IMPORTANTES :
1. Commence par une phrase d'introduction claire qui répond directement à la question
2. Explique les principes juridiques en langage simple (comme si tu parlais à quelqu'un qui n'est pas juriste)
3. Base-toi UNIQUEMENT sur le contexte juridique fourni ci-dessus
4. Structure ta réponse en 2-3 paragraphes maximum (150-250 mots)
5. Ne cite PAS les numéros d'articles (ils seront ajoutés automatiquement après)
6. Termine par un conseil pratique ou une recommandation

RÉPONSE EN FRANÇAIS :"""

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 400,
                    "top_p": 0.9,
                    "stop": ["\n\nQUESTION", "\n\nCONTEXTE"]
                }
            },
            timeout=180
        )

        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "").strip()
            
            # Nettoyer la réponse
            answer = answer.replace("RÉPONSE EN FRANÇAIS:", "").strip()
            answer = answer.replace("Réponse :", "").strip()
            
            print(f"✅ Réponse juridique reçue ({len(answer)} caractères)")
            return answer
        else:
            print(f"❌ Erreur Ollama : Status {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("❌ Timeout Ollama (180s dépassé)")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Ollama n'est pas démarré. Lancez : ollama serve")
        return None
    except Exception as e:
        print(f"❌ Erreur Ollama : {str(e)[:100]}")
        return None


# =======================
# 🧾 Mise en forme finale
# =======================
def format_ai_response_with_sources(ai_response: str, context: str) -> str:
    """
    Formate la réponse IA + ajoute les articles à la fin
    """
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

    for i, article in enumerate(articles[:3], 1):
        lines = article.split('\n')
        if len(lines) >= 2:
            reference = lines[0].strip()
            content = ' '.join(lines[1:]).strip()
            if len(content) > 250:
                content = content[:250] + "..."
            formatted += f"\n**{i}. {reference}**\n> {content}\n"

    formatted += "\n---\n_💼 Source : Base de données juridique marocaine "
    return formatted


# =======================
# 🧩 Fallback sans IA
# =======================
def generate_smart_fallback(question: str, context: str) -> str:
    """
    Génère une réponse basique si Ollama ne répond pas
    """
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

    intro += "---\n📌 **Remarque :** Cette réponse est basée sur les textes juridiques marocains en vigueur. Pour une interprétation détaillée, consultez un avocat.\n\n_💼 Source : Base de données juridique marocaine_"
    return intro