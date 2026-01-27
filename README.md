# Glyphlock

This module contains a simple implementation of **glyph-based file obfuscation**
with optional access control.

---

## What glyphlock does

Glyphlock converts a file into a deterministic representation made up of
Unicode Egyptian hieroglyphs.

The original file:
- is removed
- is replaced with a `.glyph` file
- is no longer readable as plain text

The transformation is fully reversible and does not modify the original data.

---

## What glyphlock is for

Glyphlock is meant to prevent **accidental or casual access** to files.

It is useful when:
- files should not be readable at a glance
- sensitive data should not be opened unintentionally
- projects need to be parked safely on disk
- access should require intent

This tool is **not encryption** and is not designed to protect against
determined offline attacks.

---

## Access control

Glyphlock supports optional access gating.

When enabled:
- a password is required to decode files
- passwords are verified using a key derivation function
- passwords are never stored directly

An optional recovery key can also be generated.

The recovery key:
- is shown once
- is stored as a hash
- can be used if the password is lost

If both the password and recovery key are lost, the file cannot be recovered.

---

## File behavior

When encoding:
- the original file is replaced with `filename.glyph`
- the original file extension is stored in the header
- file permissions are preserved
- the file payload is checksummed

When decoding:
- the original file is restored exactly
- permissions are restored
- corrupted or modified files fail to decode

All file operations use atomic replacement to minimize the risk of data loss.

---

## How to use this module

Glyphlock is used as a command-line tool.

Encode a single file:

```bash
glyphlock encode file.txt
```

Decode a file:

```bash
glyphlock decode file.glyph
```

Encode a directory with a password and recovery key:

```bash
glyphlock encode-dir project --lock --recovery
```

Decode a directory:

```bash
glyphlock decode-dir project
```
