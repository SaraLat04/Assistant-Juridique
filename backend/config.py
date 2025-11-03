import os
from dotenv import load_dotenv

# Load environment variables from a local .env file if present
load_dotenv()

from dotenv import load_dotenv

load_dotenv()

# ✅ Configuration LLM Local (Llama 3.2)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
# API keys and tokens (never hardcode secrets here)
HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# App configuration
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
TOP_K = 3
CHROMA_DIR = "./chroma_data"
COLLECTION_NAME = "lois_maroc"