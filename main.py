from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# Internal imports from your existing modules
from app.database.supabase import get_pending_drafts, update_sent_draft, save_draft_to_db
from app.knowledge.retrieval import retrieve_relevant_knowledge  # Adjust to match your retrieval function name
from app.gmail.service import send_email_via_gmail

app = FastAPI(title="Email Reply Agent API")

# Enable CORS so your Vercel frontend can talk to Railway backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Data Models ---
class SendEmailPayload(BaseModel):
    draft_id: str
    recipient: EmailStr
    final_content: str
    subject: str = "Re: Course Inquiry"

class GenerateDraftPayload(BaseModel):
    sender: EmailStr
    query: str


# --- API Routes ---
@app.get("/")
def home():
    return {"status": "online", "message": "Email Reply Agent API is running!"}


@app.get("/api/drafts")
def list_drafts():
    """Fetches all drafts awaiting human review for the Vercel UI."""
    try:
        return get_pending_drafts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
def create_draft(payload: GenerateDraftPayload):
    """
    1. Retrieves program context using RAG
    2. Crafts an AI response
    3. Saves the initial draft into Supabase
    """
    try:
        # Step 1: Get relevant vector context
        context = retrieve_relevant_knowledge(payload.query)
        
        # Step 2: Draft AI response (replace with your Phase 4 generation function)
        ai_draft = f"Hello,\n\nBased on your query regarding '{payload.query}', here is the information:\n{context}\n\nBest regards,"
        
        # Step 3: Save to Supabase tracking table
        record = save_draft_to_db(
            sender=payload.sender,
            query=payload.query,
            context=str(context),
            ai_draft=ai_draft
        )
        return {"status": "success", "draft": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/send")
def approve_and_send(payload: SendEmailPayload):
    """
    1. Sends the human-approved/edited email via SMTP
    2. Updates Supabase status to 'sent' and logs final_sent_content
    """
    try:
        # Step 1: Send outgoing email via Gmail SMTP
        send_email_via_gmail(
            to=payload.recipient, 
            body=payload.final_content, 
            subject=payload.subject
        )
        
        # Step 2: Log final sent version in Supabase
        update_sent_draft(
            draft_id=payload.draft_id, 
            final_content=payload.final_content
        )
        
        return {"status": "success", "message": "Email sent and draft status updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))