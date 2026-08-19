import os
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

supabase : Client = create_client(SUPABASE_URL, SUPABASE_KEY)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
genai.configure(api_key=GEMINI_API_KEY)

def retrieve_relevant_knowledge(query: str, top_k: int = 3):
    query_embedding = embedding_model(query, convert_to_numpy=True).tolist()

    response = supabase.rpc(
        "match_documents",
        {"query_embedding": query_embedding, "match_threshold": 0.3, "match_count": top_k}
    ).execute()
    return response.data if response.data else []

def generate_email_reply(user_email_text: str) -> str:
    # Retrieve context from Supabase
    docs = retrieve_relevant_knowledge(user_email_text)
    
    # Format context for prompt
    context_str = ""
    for doc in docs:
        context_str += f"- Course: {doc.get('course_name')}\n"
        context_str += f"  Description: {doc.get('course_description')}\n"
        context_str += f"  Content: {doc.get('content')}\n\n"
    
    # Construct System Prompt
    prompt = f"""
You are a helpful email reply assistant for an educational platform.
Answer the user's email inquiry politely using ONLY the context provided below.

Retrieved Context from Knowledge Base:
{context_str if context_str else "No specific course details found."}

User Email Inquiry:
"{user_email_text}"

Draft a clear, professional email reply:
"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    sample_email = "Hi, what are the prerequisites for the advanced Python course?"
    print(f"\n--- Testing Phase 4 Email Generation ---")
    print(f"Incoming Email: {sample_email}\n")
    
    reply = generate_email_reply(sample_email)
    print("--- Generated Reply Draft ---\n")
    print(reply)
        
    