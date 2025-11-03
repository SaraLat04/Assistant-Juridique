from flask import Blueprint, request, jsonify
from services.llm_service import ask_juridique
from services.vector_db import init_chroma
from services.conversation_db import init_db, create_conversation, add_message, get_conversation, list_conversations
from config import TOP_K
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

# ================================
# ⚙️ Initialisation de ChromaDB
# ================================

client, collection = init_chroma()

# Initialiser la DB d'historique
init_db()

# ================================
# 🎯 Seuil de pertinence
# ================================
SIMILARITY_THRESHOLD = 0.3  # Réduit pour accepter plus de résultats


# ================================
# 💬 Endpoint principal : /ask
# ================================
@chat_bp.route('/ask', methods=['POST'])
def ask():
    """
    Endpoint pour poser une question juridique.
    MODE JURIDIQUE UNIQUEMENT - Toujours avec références.
    """
    try:
        data = request.json
        question = data.get('question', '').strip()
        conversation_id = data.get('conversation_id')  # optionnel

        if not question:
            return jsonify({
                "error": "❌ Question manquante.",
                "question": ""
            }), 400

        print(f"\n🔍 Question reçue : {question}")

        # Créer une conversation si besoin
        if not conversation_id:
            title = (question[:80] + '...') if len(question) > 80 else question
            conversation_id = create_conversation(title=title)

        # Enregistrer le message utilisateur
        try:
            add_message(conversation_id, 'user', question, datetime.utcnow().isoformat())
        except Exception as e:
            print(f"⚠️ Erreur enregistre message utilisateur : {e}")

        # Recherche dans la base ChromaDB
        print(f"🔎 Recherche dans ChromaDB (Top {TOP_K})...")
        results = collection.query(
            query_texts=[question],
            n_results=TOP_K
        )

        # Récupération des résultats
        distances = results.get('distances', [[]])[0]
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]

        # 🔍 DEBUG : Afficher TOUS les résultats
        print(f"\n🐛 DEBUG - Tous les résultats (avant filtrage) :")
        for i, (dist, doc, meta) in enumerate(zip(distances, documents, metadatas), 1):
            similarity = 1 - (dist / 2)
            print(f"\n   📄 Résultat {i}:")
            print(f"      Distance: {dist:.4f}")
            print(f"      Similarité: {similarity:.4f}")
            print(f"      Source: {meta.get('doc', meta.get('source', 'N/A'))}")
            print(f"      Article: {meta.get('article', 'N/A')}")
            print(f"      Extrait: {doc[:100]}...")

        # Filtrer selon le seuil de similarité
        relevant_docs = []
        relevant_metas = []

        print(f"\n📊 Filtrage (seuil = {SIMILARITY_THRESHOLD}) :")
        for i, distance in enumerate(distances):
            # Convertir distance en similarité (0-1)
            similarity = 1 - (distance / 2)
            
            if similarity >= SIMILARITY_THRESHOLD:
                relevant_docs.append(documents[i])
                relevant_metas.append(metadatas[i])
                print(f"   ✅ Document {i+1} : pertinent (similarité={similarity:.3f})")
            else:
                print(f"   ❌ Document {i+1} : non pertinent (similarité={similarity:.3f})")

        nb_results = len(relevant_docs)
        print(f"\n📊 Total articles pertinents : {nb_results}")

        # ================================
        # ⚖️ MODE JURIDIQUE UNIQUEMENT
        # ================================

        if nb_results == 0:
            # Aucun article trouvé → Message d'erreur clair
            print("❌ Aucun article pertinent trouvé dans la base")
            
            answer = """❌ **Aucun article pertinent trouvé**

Votre question ne semble pas correspondre aux documents juridiques disponibles dans notre base de données.

💡 **Suggestions :**
- Reformulez votre question de manière plus précise
- Utilisez des termes juridiques (ex: "vol", "divorce", "contrat", "héritage")
- Vérifiez l'orthographe

📚 **Domaines couverts :**
- Code pénal marocain
- Code civil
- Code de la famille
- Code du travail
- Code de commerce

_💼 Assistant Juridique Marocain_"""

            # Enregistrer la réponse
            try:
                add_message(conversation_id, 'bot', answer, datetime.utcnow().isoformat())
            except Exception as e:
                print(f"⚠️ Erreur enregistre réponse bot : {e}")

            return jsonify({
                "question": question,
                "answer": answer,
                "sources_count": 0,
                "mode": "juridique",
                "status": "no_results",
                "conversation_id": conversation_id
            })

        else:
            # Articles trouvés → Génération de la réponse juridique
            print("⚖️ Mode juridique activé → Génération de la réponse avec LLM")

            # Construire le contexte
            context = ""
            for i, doc in enumerate(relevant_docs):
                meta = relevant_metas[i]
                doc_name = str(meta.get('doc', meta.get('source', 'Document inconnu'))).strip()
                article = str(meta.get('article', 'Article sans titre')).strip()
                doc_text = str(doc).strip()

                context += f"{doc_name} - {article}\n{doc_text}\n\n"

            print(f"📝 Contexte construit : {len(context)} caractères")

            # Générer la réponse avec LLM + références
            answer = ask_juridique(question, context)

            print(f"✅ Réponse générée avec succès ({len(answer)} caractères)")

            # Enregistrer la réponse
            try:
                add_message(conversation_id, 'bot', answer, datetime.utcnow().isoformat())
            except Exception as e:
                print(f"⚠️ Erreur enregistre réponse bot : {e}")

            return jsonify({
                "question": question,
                "answer": answer,
                "sources_count": nb_results,
                "mode": "juridique",
                "status": "success",
                "conversation_id": conversation_id
            })

    except Exception as e:
        print(f"❌ Erreur serveur : {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": f"Erreur serveur : {str(e)}",
            "question": question if 'question' in locals() else ""
        }), 500


# ================================
# 🗂️ Endpoints d'historique
# ================================

@chat_bp.route('/conversations', methods=['POST'])
def create_conv():
    data = request.json or {}
    title = data.get('title')
    conv_id = create_conversation(title=title)
    return jsonify({"conversation_id": conv_id}), 201


@chat_bp.route('/conversations', methods=['GET'])
def list_conv():
    convs = list_conversations()
    return jsonify(convs)


@chat_bp.route('/conversations/<conv_id>', methods=['GET'])
def get_conv(conv_id):
    conv = get_conversation(conv_id)
    if not conv:
        return jsonify({"error": "Conversation introuvable"}), 404
    return jsonify(conv)


@chat_bp.route('/conversations/<conv_id>/messages', methods=['POST'])
def post_message(conv_id):
    data = request.json or {}
    role = data.get('role')
    text = data.get('text')
    timestamp = data.get('timestamp')
    if not role or not text:
        return jsonify({"error": "role et text sont requis"}), 400
    try:
        add_message(conv_id, role, text, timestamp)
        return jsonify({"status": "ok"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================
# 🩺 Endpoint de santé
# ================================
@chat_bp.route('/health', methods=['GET'])
def health():
    """
    Vérifie que l'assistant et la base juridique sont opérationnels.
    """
    try:
        return jsonify({
            "status": "✅ OK",
            "collection": collection.name,
            "documents_count": collection.count(),
            "mode": "juridique_uniquement"
        })
    except Exception as e:
        return jsonify({
            "status": "❌ Erreur",
            "error": str(e)
        }), 500