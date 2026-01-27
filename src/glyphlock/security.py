#glyphlock/security.py
import getpass
import hashlib
import secrets
from typing import Optional, Tuple

from .headers import LockInfo, RecoveryInfo
from .errors import AccessDenied


class AccessController:
    def __init__(self):
        self._unlocked = False

    def derive_key(self, password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt, 200_000
        )

    def create_lock(self, password: str) -> LockInfo:
        salt = secrets.token_bytes(16)
        return LockInfo(salt, self.derive_key(password, salt))

    def create_recovery(self) -> Tuple[RecoveryInfo, str]:
        token = f"GLYPHLOCK-RECOVER-{secrets.token_hex(24)}"
        return RecoveryInfo(
            hashlib.sha256(token.encode()).digest()
        ), token

    def verify(
        self,
        lock: Optional[LockInfo],
        recovery: Optional[RecoveryInfo],
        password: Optional[str]
    ) -> None:
        if lock is None or self._unlocked:
            return

        if password:
            if secrets.compare_digest(
                self.derive_key(password, lock.salt),
                lock.password_hash,
            ):
                self._unlocked = True
                return

        if recovery:
            token = getpass.getpass(
                "Password invalid. Enter recovery key (leave empty to abort): "
            )
            if not token:
                raise AccessDenied("access denied")
            if token and secrets.compare_digest(
                hashlib.sha256(token.encode()).digest(),
                recovery.recovery_hash,
            ):
                self._unlocked = True
                return

        raise AccessDenied("access denied")

