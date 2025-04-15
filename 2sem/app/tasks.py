import base64
from app.core import celery_app
from app.services import HuffmanEncoder, XORCipher


@celery_app.task(name="async_encode", bind=True)
def async_encode(self, text: str, key: str):
    """Асинхронная задача кодирования текста"""
    try:
        text = str(text) if text is not None else ""

        if not text:
            return {
                "encoded_data": "",
                "key": key,
                "huffman_codes": {},
                "padding": 0
            }

        huffman_codes = HuffmanEncoder.get_huffman_codes(text)
        encoded_bits = HuffmanEncoder.huffman_encode(text, huffman_codes)

        # паддинг
        bit_length = len(encoded_bits)
        padding = (8 - (bit_length % 8)) % 8
        padded_bits = encoded_bits + '0' * padding

        # конвертируем в байты
        encoded_bytes = bytearray()
        for i in range(0, len(padded_bits), 8):
            byte_str = padded_bits[i:i + 8]
            encoded_bytes.append(int(byte_str, 2))

        # конвертируем в строку
        xor_input = encoded_bytes.decode('latin-1')

        encrypted_bytes = XORCipher.xor_encrypt(xor_input, key)

        encoded_data = base64.b64encode(encrypted_bytes).decode('utf-8')

        return {
            "encoded_data": encoded_data,
            "key": key,
            "huffman_codes": huffman_codes,
            "padding": padding
        }
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
        raise
