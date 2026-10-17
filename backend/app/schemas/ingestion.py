from typing import Literal

from pydantic import BaseModel, Field, ConfigDict, field_validator


Intent = Literal[
    "greetings",
    "farewell",
    "thank",
    "order_tracking",
    "payment_issue",
    "complaint",
    "suggestion",
    "general_question",
    "other",
]

RiskProfile = Literal[
    "low",
    "medium",
    "high",
    "unknown",
]

Priority = Literal[
    "low",
    "medium",
    "high",
]


class IngestionSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        min_length=1,
        max_length=5000,
        description="The user's original message",
        examples=["Where is my order?"],
    )

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty")
        return value


class TokenMetaData(BaseModel):
    estimated_input_tokens: int = Field(default=0, ge=0)
    note: str = (
        "Estimating the number of input tokens for the message"
    )


class IngestionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent
    risk_profile: RiskProfile
    priority: Priority
    required_actions: bool
    summary: str = Field(min_length=1, max_length=1000)
    token_meta_data: TokenMetaData = Field(
        default_factory=TokenMetaData
    )


class ResponseResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent
    summary: str = Field(min_length=1, max_length=1000)
    answer_markdown: str = Field(min_length=1)
