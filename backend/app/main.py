
import traceback
import uuid
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import APIError
from pydantic import BaseModel, Field, ValidationError

from app.schemas.ingestion import IngestionSchema, ResponseResult
from app.schemas.assistant import AssistantResult

from app.services.llm_services import (
    analyze_message,
    generate_response as generate_context_response,
)

from app.services.response_service import (
    generate_response as generate_response_from_intent,
)

from app.services.supabase_client import supabase
from app.utils.token_counter import estimate_tokens


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Enterprise Structured Ingestion Firewall",
    description="Intent detection, AI responses, and conversation memory.",
    version="4.0.0",
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

allowed_origins = [
    frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(allowed_origins)),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# CHAT REQUEST SCHEMA
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)
    session_id: str | None = None


# --------------------------------------------------
# SUPABASE CHAT MEMORY
# --------------------------------------------------

def save_message(session_id: str, role: str, content: str):
    """Save a message in Supabase."""

    supabase.table("chat_messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content,
    }).execute()


def get_chat_history(session_id: str) -> list[dict[str, str]]:
    """Get previous messages from Supabase."""

    result = (
        supabase.table("chat_messages")
        .select("role, content")
        .eq("session_id", session_id)
        .order("id")
        .execute()
    )

    return [
        {
            "role": item["role"],
            "content": item["content"],
        }
        for item in result.data
    ]


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI Response Generator API is running",
    }


# --------------------------------------------------
# CREATE NEW CHAT SESSION
# --------------------------------------------------

@app.post("/api/chat/new")
def new_chat():

    session_id = str(uuid.uuid4())

    print("NEW SESSION CREATED:", session_id, flush=True)

    return {
        "session_id": session_id,
        "message": "New chat created successfully",
    }


# --------------------------------------------------
# CHAT ENDPOINT WITH AI AND MEMORY
# --------------------------------------------------

@app.post("/api/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty.",
        )

    session_id = request.session_id or str(uuid.uuid4())

    try:
        # Load previous conversation
        history = get_chat_history(session_id)

        print("SESSION ID:", session_id, flush=True)
        print("HISTORY BEFORE AI:", history, flush=True)

        # Analyze user message
        analysis = analyze_message(message)

        # Estimate tokens
        analysis.token_meta_data.estimated_input_tokens = (
            estimate_tokens(message)
        )

        # Generate AI response using conversation history
        answer = generate_context_response(
            message=message,
            intent=str(analysis.intent),
            summary=analysis.summary,
            chat_history=history,
        )

        if not answer or not answer.strip():
            raise HTTPException(
                status_code=502,
                detail="The AI provider returned an empty response.",
            )

        answer = answer.strip()

        # Save user and AI messages
        save_message(session_id, "user", message)
        save_message(session_id, "assistant", answer)

        # Retrieve updated conversation
        updated_history = get_chat_history(session_id)

        print("CHAT COMPLETED SUCCESSFULLY", flush=True)

        return {
            "session_id": session_id,
            "intent": analysis.intent,
            "summary": analysis.summary,
            "response_markdown": answer,
            "chat_history": updated_history,
        }

    except HTTPException:
        raise

    except APIError as exc:
        print("GROQ API ERROR:", str(exc), flush=True)
        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail="AI provider request failed. Please try again later.",
        ) from exc

    except Exception as exc:
        print("CHAT ERROR:", str(exc), flush=True)
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred. Check backend logs.",
        ) from exc


# --------------------------------------------------
# ANALYZE ENDPOINT
# --------------------------------------------------

@app.post("/api/analyze", response_model=AssistantResult)
def analyze(request: IngestionSchema):

    message = request.message.strip()

    try:
        result = analyze_message(message)

        result.token_meta_data.estimated_input_tokens = (
            estimate_tokens(message)
        )

        answer = generate_response_from_intent(result)

        return AssistantResult(
            **result.model_dump(),
            response_markdown=answer,
        )

    except ValidationError as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail="Response validation failed.",
        ) from exc

    except Exception as exc:
        print("ANALYZE ERROR:", str(exc), flush=True)
        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail="Analysis failed. Please check backend logs.",
        ) from exc


# --------------------------------------------------
# RESPOND ENDPOINT
# --------------------------------------------------

@app.post("/api/respond", response_model=ResponseResult)
def respond(request: IngestionSchema):

    message = request.message.strip()

    try:
        analysis = analyze_message(message)

        analysis.token_meta_data.estimated_input_tokens = (
            estimate_tokens(message)
        )

        answer = generate_response_from_intent(analysis)

        if not answer or not answer.strip():
            raise ValueError("Generated answer is empty.")

        return ResponseResult(
            intent=analysis.intent,
            summary=analysis.summary,
            answer_markdown=answer.strip(),
        )

    except ValidationError as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail="Response validation failed.",
        ) from exc

    except Exception as exc:
        print("RESPOND ERROR:", str(exc), flush=True)
        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail="Response generation failed. Please check backend logs.",
        ) from exc
