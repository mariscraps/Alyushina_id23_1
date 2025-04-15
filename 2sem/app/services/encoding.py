import base64
from collections import defaultdict, Counter
import heapq


class HuffmanEncoder:
    @staticmethod
    def build_huffman_tree(text):
        if not text:
            return []

        frequency = Counter(text)

        # особый случай: когда все символы одинаковые
        if len(frequency) == 1:
            char = next(iter(frequency))
            print(
                f"Single char: {char} (type: {type(char)})")
            return [[char, "0"]]

        heap = [[weight, [char, ""]] for char, weight in frequency.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            lo = heapq.heappop(heap)  # самый легкий (то есть редкий) элемент
            hi = heapq.heappop(heap)  # второй по легкости
            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

        return heap[0][1:] if heap else []

    @staticmethod
    def get_huffman_codes(text):
        if not text:
            return {}

        text = str(text)
        print(f"Processing text in get_huffman_codes: {text}")

        huffman_tree = HuffmanEncoder.build_huffman_tree(text)

        # делаем обработку случая с одним символом
        if len(huffman_tree) == 1:
            char, code = huffman_tree[0]
            return {str(char): code if code else '0'}

        # преобразуем дерево в словарь кодов:
        return {str(char): code for char, code in huffman_tree}

    @staticmethod
    def huffman_encode(text, codes):
        if not text or not codes:
            return ""

        if len(codes) == 1:
            char = next(iter(codes))
            return '0' * len(text)  # возвращаем последовательность нулей

        return ''.join([codes[char] for char in text])

    @staticmethod
    def huffman_decode(encoded_bits, codes):

        # меняем местами ключи и значения, чтобы по коду находить символ:
        inv_codes = {v: k for k, v in codes.items()}
        current_code = ""
        decoded_text = []

        for bit in encoded_bits:
            current_code += bit
            if current_code in inv_codes:
                decoded_text.append(inv_codes[current_code])
                current_code = "" # сбрасываем и ищем следующее кодовое обозначение

        return ''.join(decoded_text)


class XORCipher:
    @staticmethod
    def xor_encrypt(text, key):
        if not key:
            raise ValueError("Key cannot be empty")

        # преобразуем строку в байты
        if isinstance(text, str):
            text = text.encode('latin-1')
        if isinstance(key, str):
            key = key.encode('latin-1')

        encrypted = bytearray()
        for i, char in enumerate(text):
            encrypted.append(char ^ key[i % len(key)])

        return bytes(encrypted)

    @staticmethod
    def xor_decrypt(encrypted_text, key):
        return XORCipher.xor_encrypt(encrypted_text, key)
