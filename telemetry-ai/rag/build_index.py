import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

def build_faiss_index():
    # Load metadata
    with open("data/parameter_metadata.json") as f:
        metadata = json.load(f)

    parameter_names = list(metadata.keys())
    descriptions = [
        f"{name}: {metadata[name]['description']}"
        for name in parameter_names
    ]

    # Load embedding model
    model = SentenceTransformer(MODEL_NAME)

    # Generate embeddings
    embeddings = model.encode(descriptions, convert_to_numpy=True)

    # Normalize embeddings
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    # Create CPU FAISS  index
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Save index and parameter names
    faiss.write_index(index, "data/faiss.index")

    with open("data/parameter_names.json", "w") as f:
        json.dump(parameter_names, f)

    print("FAISS index built with", len(parameter_names), "parameters")

if __name__ == "__main__":
    build_faiss_index()
