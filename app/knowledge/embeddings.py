from sentence_transformers import SentenceTransformer

def get_embedding_model():
    # Using a pre-trained model for embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def generate_embedding(text: str, model) -> list[float]:
    # Generate embedding for a given text
    embedding = model.encode(text).tolist()
    return embedding