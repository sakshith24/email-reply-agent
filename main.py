import os
from fastapi import FastAPI, HTTPException, Header ,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr


from app.database.supabase import get_pending_drafts, update_sent_draft, save_draft_to_db
from app.knowledge.retrieval import retrieve_relevant_knowledge  # Adjust to match your retrieval function name
from app.gmail.service import send_email_via_gmail
import resend
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# resend.api_key=os.getenv("RESEND_API_KEY")

app = FastAPI(title="Email Reply Agent API")

origins = [
    "https://email-reply-agent-lac.vercel.app/",
    "http://localhost:5173",
    "http://localhost:3000",
]

# Enabling CORS for  Vercel frontend and Railway backend to talk
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_SECRET_KEY", "my-default-secret-key")

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401 ,detail= "Unauthorized :Invalid API key")
    return x_api_key

class SendEmailPayload(BaseModel):
    draft_id: str
    recipient: EmailStr
    final_content: str
    subject: str = "Re: Course Inquiry"

class GenerateDraftPayload(BaseModel):
    sender: EmailStr
    query: str

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
        context = retrieve_relevant_knowledge(payload.query)
        ai_draft = f"Hello,\n\nBased on your query regarding '{payload.query}', here is the information:\n{context}\n\nBest regards,"
        record = save_draft_to_db(
            sender=payload.sender,
            query=payload.query,
            context=str(context),
            ai_draft=ai_draft
        )
        return {"status": "success", "draft": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/send", dependencies= [Depends(verify_api_key)])
def approve_and_send(payload: SendEmailPayload):
    """
    1. Sends the human-approved/edited email via Resend API
    2. Updates Supabase status to 'sent' and logs final_sent_content
    """
    try:
        # Removed direct smtplib call
        # send_email_via_gmail(
        #     to=payload.recipient, 
        #     body=payload.final_content, 
        #     subject=payload.subject
        # )
        resend.api_key = os.getenv("RESEND_API_KEY")

        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": ["shettysakshith3@gmail.com"],  # Must be inside a list
            "subject": payload.subject,
            "html": f"<p>{payload.final_content}</p>"
        })

        update_sent_draft(
            draft_id=payload.draft_id, 
            final_content=payload.final_content
        )
        
        return {"status": "success", "message": "Email sent and draft status updated."}
    except Exception as e:
        logger.error(f"Failed to send email via Resend: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")
