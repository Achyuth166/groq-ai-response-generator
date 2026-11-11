
from pydantic import Field

from app.schemas.ingestion import IngestionResult


class AssistantResult(IngestionResult):
    response_markdown: str = Field(
        min_length=1,
        description="LLM-generated answers formatted as Markdown",
    )
