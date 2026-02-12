import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

import os
from pathlib import Path

load_dotenv()

# Settings
Settings.embed_model = HuggingFaceEmbedding(model_name=os.getenv("EMBED_MODEL"))

# Chroma
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection(os.getenv("COLLECTION_NAME"))
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

data_path = Path("data")

print(f"Current working directory: {os.getcwd()}")
print(f"Looking for folder: {data_path.absolute()}")

if not data_path.exists():
    print("→ Folder 'data' does NOT exist!")
elif not data_path.is_dir():
    print("→ 'data' exists but is NOT a directory!")
else:
    files = list(data_path.glob("*.*"))  # non-hidden files
    hidden = list(data_path.glob(".*"))
    print(f"→ Found {len(files)} normal files and {len(hidden)} hidden files")
    if files:
        print("Files found:")
        for f in files:
            print(f"  - {f.name}")
    else:
        print("→ Directory is empty or only has hidden files!")

# Load documents
documents = SimpleDirectoryReader("data").load_data()

# Create or update index
index = VectorStoreIndex.from_documents(documents, vector_store=vector_store, show_progress=True)
print("✅ Knowledge base ingested!")