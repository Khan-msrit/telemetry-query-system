import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

# Load model once
model = SentenceTransformer(MODEL_NAME)

# Load FAISS index
index = faiss.read_index("data/faiss.index")

# Load parameter names
with open("data/parameter_names.json") as f:
    parameter_names = json.load(f)


def search_parameter(query: str, top_k: int = 1):
    """
    Semantic search for telemetry parameters.
    Returns the closest parameter name.
    """

    # Embed query
    embedding = model.encode([query], convert_to_numpy=True)

    # Normalize (same as index)
    faiss.normalize_L2(embedding)

    # Search
    scores, indices = index.search(embedding, top_k)

    best_match = parameter_names[indices[0][0]]

    return best_match
