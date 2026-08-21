# No models defined yet, but this file is created for future use based on the architecture.
from pydantic import BaseModel,EmailStr
from typing import Optional

class SendEmailPayload(BaseModel):
    draft_id: str
    final_content: str
    recipient: EmailStr

class GenerateDraftPayload(BaseModel):
    sender: EmailStr
    query: str
    