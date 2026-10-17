
import re
from dotenv import load_dotenv
from groq import Groq
import instructor
from pydantic import BaseModel, Field, EmailStr, field_validator

load_dotenv()


class UserProfile(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=18, le=100)
    email: EmailStr
    pan: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip()

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, value):
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):
            raise ValueError("Invalid PAN format")
        return value


client = instructor.from_groq(
    Groq(),
    mode=instructor.Mode.TOOLS
)

profile = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    response_model=UserProfile,
    messages=[
        {
            "role": "user",
            "content": (
                "Create a fictional user profile with a name, "
                "age between 18 and 100, an example.com email, "
                "and a fictional PAN-format string. "
                "Do not use real personal information."
            )
        }
    ],
)

print(profile.model_dump_json(indent=2))
