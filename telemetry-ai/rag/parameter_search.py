import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

# Load model once
model = SentenceTransformer(MODEL_NAME)
#model = SentenceTransformer(MODEL_NAME, local_files_only=True)

# Load FAISS index
index = faiss.read_index("data/faiss.index")

# Load parameter names
with open("data/parameter_names.json") as f:
    parameter_names = json.load(f)


def search_parameter(query: str, top_k: int = 5):
    """
    Returns top_k parameters with similarity scores
    """

    embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(embedding)

    scores, indices = index.search(embedding, top_k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        results.append({
            "parameter": parameter_names[idx],
            "score": float(score)
        })

    return results
