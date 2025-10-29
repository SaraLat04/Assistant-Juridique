from flask import Blueprint, request, jsonify
from services.llm_service import ask_juridique, ask_general
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
SIMILARITY_THRESHOLD = 0.7


# ================================
# 💬 Endpoint principal : /ask
# ================================
@chat_bp.route('/ask', methods=['POST'])
def ask():
    """
    Endpoint pour poser une question à l'assistant.
    Répond aux questions juridiques ET générales.
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

        # Créer une conversation si besoin et enregistrer le message utilisateur
        if not conversation_id:
            # utiliser un extrait de la question comme titre
            title = (question[:80] + '...') if len(question) > 80 else question
            conversation_id = create_conversation(title=title)

        try:
            add_message(conversation_id, 'user', question, datetime.utcnow().isoformat())
        except Exception as e:
            print(f"⚠️ Erreur enregistre message utilisateur : {e}")

        # Recherche dans la base ChromaDB
        results = collection.query(
            query_texts=[question],
            n_results=TOP_K
        )

        # Vérification de la pertinence
        distances = results.get('distances', [[]])[0]
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]

        # Filtrer les résultats selon le seuil de similarité
        relevant_docs = []
        relevant_metas = []

        for i, distance in enumerate(distances):
            if distance < SIMILARITY_THRESHOLD:
                relevant_docs.append(documents[i])
                relevant_metas.append(metadatas[i])

        nb_results = len(relevant_docs)
        print(f"📊 Articles pertinents trouvés : {nb_results}")

        # ================================
        # 🔀 BIFURCATION : Juridique ou Général
        # ================================

        if nb_results == 0:
            # ⭐ Question non juridique → Utiliser l'IA générale
            print("💬 Question générale détectée → Mode assistant universel")
            answer = ask_general(question)

            # Enregistrer la réponse du bot
            try:
                add_message(conversation_id, 'bot', answer, datetime.utcnow().isoformat())
            except Exception as e:
                print(f"⚠️ Erreur enregistre réponse bot : {e}")

            return jsonify({
                "question": question,
                "answer": answer,
                "sources_count": 0,
                "mode": "general",
                "conversation_id": conversation_id
            })

        else:
            # ⚖️ Question juridique → Utiliser le mode juridique
            print("⚖️ Question juridique détectée → Mode assistant juridique")

            # Construire le contexte à partir des documents pertinents
            context = ""
            for i, doc in enumerate(relevant_docs):
                meta = relevant_metas[i]
                doc_name = str(meta.get('DOC', 'Document inconnu')).strip()
                article = str(meta.get('Article', 'Article sans titre')).strip()
                doc_text = str(doc).strip()

                context += f"{doc_name} - {article}\n{doc_text}\n\n"

            print(f"📝 Taille du contexte : {len(context)} caractères")

            # Générer la réponse juridique
            answer = ask_juridique(question, context)

            print(f"✅ Réponse générée ({len(answer)} caractères).")

            # Enregistrer la réponse du bot
            try:
                add_message(conversation_id, 'bot', answer, datetime.utcnow().isoformat())
            except Exception as e:
                print(f"⚠️ Erreur enregistre réponse bot : {e}")

            return jsonify({
                "question": question,
                "answer": answer,
                "sources_count": nb_results,
                "mode": "juridique",
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
# 🗂️ Endpoints d'historique de conversation
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
# 🩺 Endpoint de santé : /health
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
            "documents_count": collection.count()
        })
    except Exception as e:
        return jsonify({
            "status": "❌ Erreur",
            "error": str(e)
        }), 500