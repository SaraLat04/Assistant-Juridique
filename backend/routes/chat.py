from flask import Blueprint, request, jsonify
from services.llm_service import ask_juridique, ask_general
from services.vector_db import init_chroma
from config import TOP_K

chat_bp = Blueprint('chat', __name__)

# ================================
# ⚙️ Initialisation de ChromaDB
# ================================
client, collection = init_chroma()

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

        if not question:
            return jsonify({
                "error": "❌ Question manquante.",
                "question": ""
            }), 400

        print(f"\n🔍 Question reçue : {question}")

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
            
            return jsonify({
                "question": question,
                "answer": answer,
                "sources_count": 0,
                "mode": "general"
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

            return jsonify({
                "question": question,
                "answer": answer,
                "sources_count": nb_results,
                "mode": "juridique"
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