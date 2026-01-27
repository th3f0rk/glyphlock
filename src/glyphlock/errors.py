#glyphlock/errors.py
class GlyphLockError(Exception):
    pass


class FormatError(GlyphLockError):
    pass


class AccessDenied(GlyphLockError):
    pass


class IntegrityError(GlyphLockError):
    pass
