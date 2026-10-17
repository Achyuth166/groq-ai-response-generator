
import re
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError


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


# Test with invalid data
try:
    user = UserProfile(
        name="",
        age=15,
        email="wrong-email",
        pan="123INVALID"
    )
    print(user.model_dump_json(indent=2))

except ValidationError as error:
    print("Validation failed:")
    print(error)
