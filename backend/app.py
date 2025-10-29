from flask import Flask
from flask_cors import CORS  # <-- ajouter ceci
from routes.chat import chat_bp
from services.vector_db import init_chroma

app = Flask(__name__)
CORS(app)  # <-- autorise toutes les origines pour le développement
app.register_blueprint(chat_bp)

# 🔹 Initialisation ChromaDB
client, collection = init_chroma()
print("✅ ChromaDB initialisée. Collection:", collection.name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
