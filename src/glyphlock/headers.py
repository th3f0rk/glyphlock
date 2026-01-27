#glyphlock/headers.py
from dataclasses import dataclass
from typing import Optional

from .errors import FormatError


@dataclass
class LockInfo:
    salt: bytes
    password_hash: bytes


@dataclass
class RecoveryInfo:
    recovery_hash: bytes


@dataclass
class GlyphHeader:
    ext: str
    mode: int
    checksum: str
    lock: Optional[LockInfo]
    recovery: Optional[RecoveryInfo]

    @classmethod
    def parse(cls, lines: list[str]) -> tuple["GlyphHeader", int]:
        try:
            ext = lines[0][5:].strip()
            mode = int(lines[1][6:], 8)
            checksum = lines[2][8:].strip()
        except Exception:
            raise FormatError("invalid glyph header")

        idx = 3
        lock = None
        recovery = None
        if idx < len(lines) and lines[idx].startswith("@lock:"):
            idx += 1
            salt = bytes.fromhex(lines[idx][6:].strip())
            idx += 1
            password_hash = bytes.fromhex(lines[idx][6:].strip())
            idx += 1
            lock = LockInfo(salt, password_hash)
        if idx < len(lines) and lines[idx].startswith("@recovery:"):
            idx += 1
            recovery_hash = bytes.fromhex(lines[idx][15:].strip())
            idx += 1
            recovery = RecoveryInfo(recovery_hash)
        return cls(ext, mode, checksum, lock, recovery), idx

    def serialize(self) -> str:
        out = (
            f"@ext:{self.ext}\n"
            f"@mode:{self.mode:04o}\n"
            f"@sha256:{self.checksum}\n"
        )
        if self.lock:
            out += (
                "@lock:pbkdf2-sha256\n"
                f"@salt:{self.lock.salt.hex()}\n"
                f"@hash:{self.lock.password_hash.hex()}\n"
            )
        if self.recovery:
            out += (
                "@recovery:sha256\n"
                f"@recovery-hash:{self.recovery.recovery_hash.hex()}\n"
            )
        return out

