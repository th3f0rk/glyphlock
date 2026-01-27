#glyphlock/filesystem.py
import os
import tempfile


class AtomicFilesystem:
    def read_bytes(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def read_lines(self, path: str) -> list[str]:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()

    def _fsync_dir(self, path: str):
        d = os.path.dirname(path) or "."
        dirfd = os.open(d, os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)

    def atomic_write(self, path: str, data: bytes | str, binary: bool):
        mode = "wb" if binary else "w"
        d = os.path.dirname(path) or "."
        fd, tmp = tempfile.mkstemp(dir=d)
        try:
            with os.fdopen(fd, mode, encoding=None if binary else "utf-8") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
            self._fsync_dir(path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

