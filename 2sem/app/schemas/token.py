from pydantic import BaseModel
from pydantic import Field


class Token(BaseModel):
    id: int = Field(..., example=1, description="User ID")
    email: str = Field(..., example="user@example.com",
                       description="User email")
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                       description="JWT token")
    token_type: str = Field(default="bearer", example="bearer",
                            description="Token type")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenWithUser(BaseModel):
    id: int = Field(..., example=1, description="User ID")
    email: str = Field(..., example="user@example.com",
                       description="User email")
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                       description="JWT token")
    token_type: str = Field(default="bearer", example="bearer",
                            description="Token type")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    email: str | None = None
