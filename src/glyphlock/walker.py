#glyphlock/walker.py
import os
from typing import Iterable


class FileWalker:
    def iter_files(self, root: str) -> Iterable[str]:
        for dp, _, fnames in os.walk(root):
            for n in fnames:
                p = os.path.join(dp, n)
                if not os.path.islink(p):
                    yield p

