from pydantic import BaseModel, Field
from typing import Dict, Optional


class EncodeRequest(BaseModel):
    text: str
    key: str

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello World",
                "key": "secret"
            }
        }


class EncodeResponse(BaseModel):
    encoded_data: str = Field(..., description="Base64 encoded string")
    key: str = Field(..., description="Encryption key used")
    huffman_codes: Dict[str, str] = Field(...,
        description="Dictionary of Huffman codes for characters")
    padding: int = Field(..., description="Number of padding bits added")

    class Config:
        json_schema_extra = {
            "example": {
                "encoded_data": "SGVsbG8sIFdvcmxkIQ==",
                "key": "secret",
                "huffman_codes": {
                    "H": "00",
                    "e": "01",
                    "l": "10",
                    "o": "110",
                    ",": "1110",
                    " ": "11110",
                    "W": "111110",
                    "r": "1111110",
                    "d": "1111111",
                    "!": "11111111"
                },
                "padding": 3
            }
        }


class TaskResponse(BaseModel):
    message: str
    task_id: str
    status_check_url: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Encoding task started",
                "task_id": "50a0a2a0",
                "status_check_url": "/api/tasks/50a0a2a0"
            }
        }


class DecodeRequest(BaseModel):
    encoded_data: str = Field(..., example="SGVsbG8sIFdvcmxkIQ==",
                              description="Base64 encoded data")
    key: str = Field(..., example="secret", description="Encryption key")
    huffman_codes: Dict[str, str] = Field(
        ...,
        example={"H": "00", "e": "01", "l": "10", "o": "110"},
        description="Huffman codes mapping"
    )
    padding: int = Field(..., example=3, description="Number of padding bits")

    class Config:
        schema_extra = {
            "example": {
                "encoded_data": "SGVsbG8sIFdvcmxkIQ==",
                "key": "secret",
                "huffman_codes": {"H": "00", "e": "01", "l": "10", "o": "110"},
                "padding": 3
            }
        }


class DecodeResponse(BaseModel):
    decoded_text: str

    class Config:
        json_schema_extra = {
            "example": {
                "decoded_text": "Hello, World!"
            }
        }


class WsEncodeRequest(BaseModel):
    text: str
    key: str
    token: str


class TaskStatus(BaseModel):
    task_id: str = Field(..., example="50a0a2a0", description="Unique task identifier")
    status: str = Field(
        ...,
        example="PENDING",
        description="Task status: PENDING|SUCCESS|FAILURE",
        enum=["PENDING", "SUCCESS", "FAILURE"]
    )
    result: Optional[EncodeResponse] = Field(
        None,
        description="Result when task is completed")
    error: Optional[str] = Field(
        None,
        example=None,
        description="Error message if task failed")

    class Config:
        schema_extra = {
            "$ref": "#/components/schemas/TaskStatus",
            "example": {
                "task_id": "50a0a2a0",
                "status": "PENDING",
                "result": None,
                "error": None
            }
        }