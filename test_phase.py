import os
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import time
from google.api_core import exceptions
from openai import OpenAI
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase : Client = create_client(SUPABASE_URL, SUPABASE_KEY)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
genai.configure(api_key=GEMINI_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def retrieve_relevant_knowledge(query: str, top_k: int = 3):
    # Ensure query is encoded properly as a list or string via model.encode
    query_embedding = embedding_model.encode(query, convert_to_numpy=True).tolist()
    
    response = supabase.rpc(
        "match_documents",
        {"query_embedding": query_embedding, "match_threshold": 0.3, "match_count": top_k}
    ).execute()
    
    return response.data if response.data else []
def generate_email_reply_with_openai(prompt:str) -> str:
    """Fallback function if gemini fails to respond"""
    print("\n[Fallback] Gemini failed . Attempting generation using OpenAI")
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
    )
    return response.choices[0].message.content

def generate_email_reply_with_retry(user_email_text: str) -> str:
    docs = retrieve_relevant_knowledge(user_email_text)
    
    context_str = ""
    for doc in docs:
        context_str += f"- Course: {doc.get('course_name')}\n"
        context_str += f"  Description: {doc.get('course_description')}\n"
        context_str += f"  Content: {doc.get('content')}\n\n"
    
    prompt = f"""
 You are a helpful email reply assistant for an educational platform.
 Answer the user's email inquiry politely using ONLY the context provided below.

 Retrieved Context from Knowledge Base:
 {context_str if context_str else "No specific course details found."}

 User Email Inquiry:
 "{user_email_text}"

 Draft a clear, professional email reply:
 """

    model = genai.GenerativeModel("gemini-3.6-flash")
    
    # Retry loop to handle 429 rate limit errors
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except exceptions.ResourceExhausted:
            print(f"Rate limit hit! Waiting 16 seconds before retry {attempt + 1}/3...")
            time.sleep(10)
            
        raise Exception("Failed to generate response after 3 retries due to rate limits.")
    try:
        return generate_email_reply_with_openai(prompt)
    except Exception as fallback_err:
        raise Exception(f"Both Gemini and OpenAI failed to generate a response. Error: {fallback_err}"
        )

if __name__ == "__main__":
    sample_email = "Hi, what are the prerequisites for the advanced Python course?"
    print("\n--- Testing Phase 4 Email Generation ---")
    print(f"Incoming Email: {sample_email}\n")
    
    # Call the new function here:
    reply = generate_email_reply_with_retry(sample_email)
    print("--- Generated Reply Draft ---\n")
    print(reply)
        
    