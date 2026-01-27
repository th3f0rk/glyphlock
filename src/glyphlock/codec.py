#glyphlock/codec.py
import base64
from typing import Dict

_GLYPH_START = 0x13000
_GLYPH_COUNT = 64
_WRAP_WIDTH = 80

_BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_BASE64_PAD = "="

_PAD_GLYPH = chr(_GLYPH_START + _GLYPH_COUNT)


class GlyphCodec:
    def __init__(self):
        glyphs = [chr(_GLYPH_START + i) for i in range(_GLYPH_COUNT)]
        self.encode_map: Dict[str, str] = dict(zip(_BASE64_ALPHABET, glyphs))
        self.decode_map: Dict[str, str] = dict(zip(glyphs, _BASE64_ALPHABET))
        self.encode_map[_BASE64_PAD] = _PAD_GLYPH
        self.decode_map[_PAD_GLYPH] = _BASE64_PAD

    def encode(self, data: bytes) -> str:
        b64 = base64.b64encode(data).decode("ascii")
        glyphs = "".join(self.encode_map[c] for c in b64)
        return "\n".join(
            glyphs[i:i + _WRAP_WIDTH]
            for i in range(0, len(glyphs), _WRAP_WIDTH)
        ) + "\n"

    def decode(self, text: str) -> bytes:
        glyphs = "".join(c for c in text if not c.isspace())
        b64 = "".join(self.decode_map[c] for c in glyphs)
        return base64.b64decode(b64, validate=True)

