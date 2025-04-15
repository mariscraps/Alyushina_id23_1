import base64
from fastapi import APIRouter, HTTPException, status, Depends
from celery.result import AsyncResult

from app.cruds.user import get_user_by_email
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.schemas.encode import (
    EncodeRequest,
    EncodeResponse,
    DecodeRequest,
    DecodeResponse,
    TaskStatus)

from app.services.encoding import HuffmanEncoder
from app.core.celery import celery_app
from app.tasks import async_encode
from app.api.auth import security_scheme


router = APIRouter()


@router.post("/encode", response_model=TaskStatus, responses={
        200: {
            "description": "Task started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "task_id": "50a0a2a0",
                        "status": "PENDING",
                        "result": None,
                        "error": None
                    }
                }
            }
        },
        400: {
            "description": "Invalid input",
            "content": {
                "application/json": {
                    "example": {"detail": "Text cannot be empty"}
                }
            }
        }
    }
)
async def encode_text(request: EncodeRequest):
    """Асинхронное кодирование"""
    try:
        if not request.text:
            raise ValueError("Text cannot be empty")


        # запускаем задачу Celery с передачей текста и ключа
        task = async_encode.delay(request.text, request.key)

        return TaskStatus(
            task_id=task.id,
            status=task.status,
            result=None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tasks/{task_id}", response_model=TaskStatus, responses={
        200: {
            "description": "Task status information",
            "content": {
                "application/json": {
                    "examples": {
                        "pending": {
                            "value": {
                                "task_id": "50a0a2a0",
                                "status": "PENDING",
                                "result": None,
                                "error": None
                            }
                        },
                        "success": {
                            "value": {
                                "task_id": "50a0a2a0",
                                "status": "SUCCESS",
                                "result": {
                                    "encoded_data": "SGVsbG8sIFdvcmxkIQ==",
                                    "key": "secret",
                                    "huffman_codes": {"H": "00", "e": "01"},
                                    "padding": 3
                                },
                                "error": None
                            }
                        },
                        "failed": {
                            "value": {
                                "task_id": "50a0a2a0",
                                "status": "FAILURE",
                                "result": None,
                                "error": "Invalid key format"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_task_status(task_id: str):
    """Check encoding task status by task_id"""
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.failed():
        return TaskStatus(
            task_id=task_id,
            status=task_result.status,
            error=str(task_result.result)
        )

    return TaskStatus(
        task_id=task_id,
        status=task_result.status,
        result=task_result.result if task_result.ready() else None
    )


@router.post("/decode", response_model=DecodeResponse)
async def decode_text(request: DecodeRequest):
    """Декодирование"""
    try:
        encrypted_bytes = base64.b64decode(request.encoded_data)

        # преобразуем ключ в байты
        key_bytes = request.key.encode('utf-8')

        # расшифровываем побайтово при помощи XOR
        decrypted_bytes = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted_bytes.append(byte ^ key_bytes[i % len(key_bytes)])

        # преобразуем расшифрованные байты в бинарную строку
        encoded_bits = ''.join(f"{byte:08b}" for byte in decrypted_bytes)

        # удаляем лишние биты (если было дополнение до 8 бит)
        if request.padding > 0:
            encoded_bits = encoded_bits[:-request.padding]

        decoded_text = HuffmanEncoder.huffman_decode(encoded_bits,
                                                     request.huffman_codes)

        return DecodeResponse(decoded_text=decoded_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
