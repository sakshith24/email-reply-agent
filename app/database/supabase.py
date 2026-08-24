import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

def get_pending_drafts():
    response = supabase.table("email_drafts").select("*").eq("status", "pending_review").execute()
    return response.data

def save_draft_to_db(sender: str, query: str, context: str, ai_draft: str):
    response = supabase.table("email_drafts").insert({
        "sender_email": sender,
        "user_query": query,
        "retrieved_context": context,
        "ai_draft_content": ai_draft,
        "status": "pending_review"
    }).execute()
    return response.data

def update_sent_draft(draft_id: str, final_content: str):
    response = supabase.table("email_drafts").update({
        "final_sent_content": final_content,
        "status": "sent"
    }).eq("id", draft_id).execute()
    return response.data