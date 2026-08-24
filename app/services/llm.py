import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions
from openai import OpenAI

load_dotenv()

# Initialize API Keys & Clients
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _call_openai_fallback(prompt: str) -> str:
    """Helper function to execute OpenAI fallback generation."""
    if not openai_client:
        raise Exception("OPENAI_API_KEY is missing from environment variables.")

    print("[FALLBACK] Gemini unavailable. Triggering OpenAI (gpt-4o-mini)...")
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def generate_email_reply(prompt: str) -> tuple[str, str]:
    """Generates an email reply using Gemini primary, falling back to OpenAI.

    Returns:
        tuple: (generated_text, provider_used)
    """
    model = genai.GenerativeModel("gemini-3.6-flash")

    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            if response.text:
                return response.text, "gemini"
        except (exceptions.ResourceExhausted, exceptions.GoogleAPIError, Exception) as e:
            print(f"[GEMINI WARNING] Attempt {attempt + 1}/3 failed: {e}")
            time.sleep(10)

    try:
        reply_text = _call_openai_fallback(prompt)
        return reply_text, "openai"
    except Exception as fallback_err:
        raise RuntimeError(f"All LLM providers failed. Details: {fallback_err}")