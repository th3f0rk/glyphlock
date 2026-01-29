# Glyphlock

This module contains a simple implementation of **glyph-based file obfuscation**
with optional access control.

---

## How to install glyphlock

Glyphlock is distributed by **PyPI**. You will need to install `pipx` since **PEP 668** doesn't 
allow for externally managed systems to be installed with `pip`. This isn't entirely 
enforced depending on how you installed Python or your operating system. 
**The guaranteed method on all systems is to use `pipx`**

To install pipx you can do
```bash
brew install pipx
pipx ensurepath
```
After running `pipx ensurepath`, reload your terminal or open a new instance.
For example if you use a zsh terminal run
```bash
exec zsh
```
Now you can install glyphlock
```bash
pipx install glyphlock
```
To verify it is installed you can do
```bash
glyphlock --help
```
or
```bash
which glyphlock
```

**NOTE**
**Glyphlock uses Unicode Egiption Hieroglyphs so for now a font where those unicode characters are included is needed**

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

It is designed to be used when:
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

Currently Glyphlock allows for a user to create an empty password. 
If the user does so they must press 'Enter' when prompted for the password.

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

## Directory handling

When operating on directories, glyphlock walks the directory tree recursively.

The following are skipped automatically:
- symbolic links
- hidden directories
- version control metadata (`.git`, `.hg`, `.svn`)
- virtual environments (`.venv`, `env`)
- Python cache directories (`__pycache__`)
- editor configuration directories

Only user-authored files are processed by default.

---

## How to use this module

Glyphlock is used as a command-line tool. Only the `encode` and `encode-directory` commands accept access flags. All commands accept `--plan` flags.

Encode a single file:

```bash
glyphlock encode file.txt
```

Decode a file (decode commands do not accept access flags):

```bash
glyphlock decode file.glyph
```

Encode a directory with a password and recovery key:

```bash
glyphlock encode-dir project --lock --recovery
```

Decode a directory (decode commands do not accept access flags):

```bash
glyphlock decode-dir project
```
---

## Access flags

The following flags are supported when encoding files or directories:

- `--lock`  
  Require a password to decode the file(s).

- `--recovery`  
  Generate a recovery key that can be used if the password is lost.

When operating on directories:
- the password is requested once per command
- the recovery key (if enabled) is generated once per command
- the same access credentials apply to all files in the operation

When operating on a single file:
- the same flags apply, but only affect that file

---

## Planning and dry runs

Glyphlock supports a `--plan` flag for all commands.

When `--plan` is used:
- no files are modified
- no passwords are requested
- no recovery keys are generated
- the operation is printed instead of executed

This allows you to preview exactly what glyphlock would do.

Examples:

```bash
glyphlock encode file.txt --plan
glyphlock encode-dir project --plan
glyphlock decode-dir project --plan
```

---

## Security note

Glyphlock is not encryption.

It is designed to prevent casual or accidental access, not to withstand
determined cryptographic attacks.

If you require strong confidentiality against an active adversary, use
established encryption tools such as age, gpg, or full-disk encryption.

