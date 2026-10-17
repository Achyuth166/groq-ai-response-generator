
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.schemas.ingestion import (
    IngestionSchema,
    IngestionResult,
    ResponseResult,
)
from app.services.llm_services import (
    analyze_message,
    generate_response,
)
from app.utils.token_counter import estimate_tokens


app = FastAPI(
    title="Enterprise Structured Ingestion Firewall",
    description="Intent detection and AI response generation.",
    version="2.0.0",
)

# Allow requests from the React development server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "AI Response Generator API is running",
    }


@app.post("/api/analyze", response_model=IngestionResult)
def analyze(request: IngestionSchema):
    message = request.message.strip()

    try:
        result = analyze_message(message)
        result.token_meta_data.estimated_input_tokens = (
            estimate_tokens(message)
        )
        return result

    except ValidationError as exc:
        print(f"Analysis validation error: {exc}", flush=True)
        raise HTTPException(
            status_code=502,
            detail="Model response validation failed.",
        ) from exc

    except Exception as exc:
        print(
            f"ANALYZE FAILED: {type(exc).__name__}: {exc}",
            flush=True,
        )
        raise HTTPException(
            status_code=502,
            detail="Message analysis failed. Check the backend terminal.",
        ) from exc


@app.post("/api/respond", response_model=ResponseResult)
def respond(request: IngestionSchema):
    message = request.message.strip()

    # Step 1: Analyze the message.
    try:
        analysis = analyze_message(message)
        print(
            f"Analysis successful. Intent: {analysis.intent}",
            flush=True,
        )
    except Exception as exc:
        print(
            f"STEP 1 FAILED - ANALYSIS: {type(exc).__name__}: {exc}",
            flush=True,
        )
        raise HTTPException(
            status_code=502,
            detail="Intent analysis failed. Check the backend terminal.",
        ) from exc

    # Step 2: Generate the AI response.
    try:
        answer = generate_response(
            message=message,
            intent=analysis.intent,
            summary=analysis.summary,
        )

        if not answer or not answer.strip():
            raise ValueError("Generated answer is empty")

        print("Step 2 successful. Answer generated.", flush=True)

    except Exception as exc:
        print(
            f"STEP 2 FAILED - GENERATION: {type(exc).__name__}: {exc}",
            flush=True,
        )
        raise HTTPException(
            status_code=502,
            detail="Answer generation failed. Check the backend terminal.",
        ) from exc

    # Step 3: Validate and return the response.
    try:
        return ResponseResult(
            intent=analysis.intent,
            summary=analysis.summary,
            answer_markdown=answer,
        )
    except ValidationError as exc:
        print(f"STEP 3 FAILED - VALIDATION: {exc}", flush=True)
        raise HTTPException(
            status_code=502,
            detail="Final response validation failed.",
        ) from exc
