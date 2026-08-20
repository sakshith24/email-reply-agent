import os
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import time
from google.api_core import exceptions
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

supabase : Client = create_client(SUPABASE_URL, SUPABASE_KEY)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
genai.configure(api_key="GEMINI_API_KEY")

def retrieve_relevant_knowledge(query: str, top_k: int = 3):
    # Ensure query is encoded properly as a list or string via model.encode
    query_embedding = embedding_model.encode(query, convert_to_numpy=True).tolist()
    
    response = supabase.rpc(
        "match_documents",
        {"query_embedding": query_embedding, "match_threshold": 0.3, "match_count": top_k}
    ).execute()
    
    return response.data if response.data else []

def generate_email_reply_openrouter(user_email_text: str) -> str:
    docs = retrieve_relevant_knowledge(user_email_text)
    
    context_str = ""
    for doc in docs:
        context_str += f"- Course: {doc.get('course_name')}\n"
        context_str += f"  Description: {doc.get('course_description')}\n\n"
    
    prompt = f"Context:\n{context_str}\n\nInquiry: {user_email_text}\n\nDraft a clear, professional reply:"

    openrouter_key = os.getenv("OPENROUTER_API_KEY") # Ensure this is in your .env file
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openrouter/free",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    
    data = response.json()
    
    # Check if OpenRouter returned an error response
    if "error" in data:
        print(f"OpenRouter Error: {data['error']}")
        raise Exception(f"OpenRouter API Failure: {data['error'].get('message')}")
        
    return data['choices'][0]['message']['content']

# def generate_email_reply_with_retry(user_email_text: str) -> str:
#     docs = retrieve_relevant_knowledge(user_email_text)
    
#     context_str = ""
#     for doc in docs:
#         context_str += f"- Course: {doc.get('course_name')}\n"
#         context_str += f"  Description: {doc.get('course_description')}\n"
#         context_str += f"  Content: {doc.get('content')}\n\n"
    
#     prompt = f"""
# You are a helpful email reply assistant for an educational platform.
# Answer the user's email inquiry politely using ONLY the context provided below.

# Retrieved Context from Knowledge Base:
# {context_str if context_str else "No specific course details found."}

# User Email Inquiry:
# "{user_email_text}"

# Draft a clear, professional email reply:
# """

#     model = genai.GenerativeModel("gemini-2.5-flash")
    
#     # Retry loop to handle 429 rate limit errors
#     for attempt in range(3):
#         try:
#             response = model.generate_content(prompt)
#             return response.text
#         except exceptions.ResourceExhausted:
#             print(f"Rate limit hit! Waiting 16 seconds before retry {attempt + 1}/3...")
#             time.sleep(16)
            
#     raise Exception("Failed to generate response after 3 retries due to rate limits.")

if __name__ == "__main__":
    sample_email = "Hi, what are the prerequisites for the advanced Python course?"
    print("\n--- Testing Phase 4 Email Generation ---")
    print(f"Incoming Email: {sample_email}\n")
    
    # Call the new function here:
    reply = generate_email_reply_openrouter(sample_email)
    print("--- Generated Reply Draft ---\n")
    print(reply)
        
    