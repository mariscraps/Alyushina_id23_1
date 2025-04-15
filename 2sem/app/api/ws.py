import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.encoding import HuffmanEncoder, XORCipher
from app.core.websocket_manager import WebSocketManager
from app.core.security import validate_ws_token
from app.schemas.encode import WsEncodeRequest
import base64
import logging

router = APIRouter()
ws_manager = WebSocketManager()
logger = logging.getLogger("websockets")


@router.websocket("/ws/encode")
async def websocket_encode(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        try:
            auth_data = await websocket.receive_text()
            token = json.loads(auth_data).get("token")
            if not validate_ws_token(token):
                await _send_error(websocket, "Invalid authentication")
                return
        except (json.JSONDecodeError, AttributeError) as e:
            await _send_error(websocket, f"Invalid auth format: {str(e)}")
            return

        # основной цикл общения с клиентом
        while True:
            data = await websocket.receive_text()
            await _process_message(websocket, data)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await _send_error(websocket, "Internal server error")
    finally:
        ws_manager.disconnect(websocket)


async def _process_message(websocket: WebSocket, data: str):
    """Обработка входящего сообщения"""
    try:

        # распаковываем входящие данные (текст и ключ)
        request = WsEncodeRequest(**json.loads(data))

        huffman_codes = HuffmanEncoder.get_huffman_codes(request.text)
        encoded_bits = HuffmanEncoder.huffman_encode(request.text,
                                                     huffman_codes)

        padding = (8 - len(encoded_bits) % 8)
        padded_bits = encoded_bits + '0' * padding
        encoded_bytes = bytes(
        int(padded_bits[i: i+8], 2)
        for i in range(0, len(padded_bits), 8))

        encrypted = XORCipher.xor_encrypt(encoded_bytes.decode('latin-1'),
                                            request.key)

        await websocket.send_json({
        "status": "success",
        "encoded_data": base64.b64encode(encrypted.encode('latin-1')).decode('utf-8'),
        "huffman_codes": huffman_codes,
        "padding": padding,
        "key": request.key
        })

    except json.JSONDecodeError:
        await _send_error(websocket, "Invalid JSON format")
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        await _send_error(websocket, f"Processing error: {str(e)}")


async def _send_error(websocket: WebSocket, message: str):
    """Отправка сообщения об ошибке"""
    await websocket.send_json({
        "status": "error",
        "message": message
    })
    await websocket.close(code=1008)  # 1008 = Policy Violation