from pydantic import BaseModel, EmailStr
from pydantic import Field


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="user@example.com",
        description="Valid email address for registration")
    password: str = Field(..., example="securepassword123",
        description="Password for the account")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123"
            }
        }


class UserLogin(UserCreate):
    pass


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "is_active": True
            }
        }
