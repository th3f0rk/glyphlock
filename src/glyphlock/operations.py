#glyphlock/operations.py
import hashlib
import os
import stat
from typing import Optional

from .codec import GlyphCodec
from .filesystem import AtomicFilesystem
from .headers import GlyphHeader, RecoveryInfo
from .security import AccessController
from .errors import IntegrityError, FormatError
from .walker import FileWalker


class GlyphLockEngine:
    def __init__(self):
        self.codec = GlyphCodec()
        self.fs = AtomicFilesystem()
        self.security = AccessController()
        self.walker = FileWalker()

    def encode_file(
        self,
        path: str,
        password: Optional[str],
        recovery: Optional[RecoveryInfo],
    ):
        if path.endswith(".glyph"):
            return

        st = os.stat(path)
        mode = stat.S_IMODE(st.st_mode)
        raw = self.fs.read_bytes(path)
        checksum = hashlib.sha256(raw).hexdigest()

        lock = self.security.create_lock(password) if password else None
        rec = recovery

        header = GlyphHeader(
            os.path.splitext(path)[1],
            mode,
            checksum,
            lock,
            rec,
        )

        out = header.serialize() + self.codec.encode(raw)
        out_path = os.path.splitext(path)[0] + ".glyph"

        self.fs.atomic_write(out_path, out, binary=False)
        os.remove(path)

    def decode_file(self, path: str, password: Optional[str]):
        try:
            lines = self.fs.read_lines(path)
        except UnicodeDecodeError:
            raise FormatError("invalid glyph file encoding")

        header, idx = GlyphHeader.parse(lines)

        self.security.verify(header.lock, header.recovery, password)

        data = self.codec.decode("".join(lines[idx:]))
        if hashlib.sha256(data).hexdigest() != header.checksum:
            raise IntegrityError("payload integrity failed")

        out_path = path[:-6] + header.ext
        self.fs.atomic_write(out_path, data, binary=True)
        os.chmod(out_path, header.mode)
        os.remove(path)

