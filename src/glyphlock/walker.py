#glyphlock/walker.py
import os
from typing import Iterable


class FileWalker:
    DEFAULT_EXCLUDED_DIRS = {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "env",
        "__pycache__",
        ".idea",
        ".vscode",
    }

    def iter_files(self, root: str) -> Iterable[str]:
        root = os.path.abspath(root)

        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d for d in dirnames
                if not self._skip_dir(d)
            ]

            for name in filenames:
                path = os.path.join(dirpath, name)

                if os.path.islink(path):
                    continue

                yield path

    def _skip_dir(self, name: str) -> bool:
        if name in self.DEFAULT_EXCLUDED_DIRS:
            return True

        if name.startswith("."):
            return True

        return False

