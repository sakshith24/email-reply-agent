from app.database.supabase import get_supabase_client
from app.knowledge.embeddings import get_embedding_model, generate_embedding

def retrieve_relevant_knowledge(query: str, table_name: str = "knowledge_base", top_k: int = 5):
    try:
        supabase = get_supabase_client()
        embedding_model = get_embedding_model()
        query_embedding = generate_embedding(query, embedding_model)

        # Perform vector search
        # This assumes you have a `vector` column in your knowledge_base table
        # and pg_vector extension is enabled in Supabase.
        response = (
            supabase.rpc(
                "match_documents",
                {"query_embedding": query_embedding, "match_threshold": 0.3, "match_count": top_k},
            )
            .execute()
        )

        if response.data:
            return response.data
        return []

    except Exception as e:
        print(f"An error occurred during knowledge retrieval: {e}")
        return []