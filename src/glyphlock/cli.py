# glyphlock/cli.py
import argparse
import getpass
import os
import sys

from .operations import GlyphLockEngine
from .errors import GlyphLockError
from .headers import GlyphHeader


def peek_header(engine: GlyphLockEngine, path: str) -> GlyphHeader:
    lines = engine.fs.read_lines(path)
    header, _ = GlyphHeader.parse(lines)
    return header


def main():
    parser = argparse.ArgumentParser(
        prog="glyphlock",
        description=(
            "Encode and decode files or directories into the .glyph format.\n\n"
            "Glyphlock is a safety-focused encoding tool with optional access control.\n"
            "Files are never modified in-place: encode replaces the original file,\n"
            "and decode restores it."
        ),
        epilog=(
            "Password behavior:\n"
            "  • Passwords are requested only when a file is protected.\n"
            "  • If no lock exists, decoding proceeds without prompts.\n"
            "  • Recovery keys are optional and shown once at encode time.\n\n"
            "Use --plan with any command to preview actions without modifying files."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
            "--version",
            action="version",
            version="glyphlock 0.1.5"
    )

    sub = parser.add_subparsers(dest="cmd", required=True)



    ef = sub.add_parser(
        "encode",
        help="Encode a single file into a .glyph file",
        description=(
            "Encode a single file into the .glyph format.\n\n"
            "The original file is removed after successful encoding.\n"
            "Directories are not allowed; use encode-dir instead."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ef.add_argument("path", help="Path to the file to encode")
    ef.add_argument(
        "--lock",
        action="store_true",
        help="Protect the encoded file with a password",
    )
    ef.add_argument(
        "--recovery",
        action="store_true",
        help="Generate a one-time recovery key (displayed once)",
    )
    ef.add_argument(
        "--plan",
        action="store_true",
        help="Show what would be encoded without modifying any files",
    )

    df = sub.add_parser(
        "decode",
        help="Decode a .glyph file back to its original form",
        description=(
            "Decode a .glyph file back to its original file.\n\n"
            "If the file is password-protected, you will be prompted.\n"
            "If no lock exists, decoding proceeds without prompts."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    df.add_argument("path", help="Path to the .glyph file to decode")
    df.add_argument(
        "--plan",
        action="store_true",
        help="Show what would be decoded without modifying any files",
    )

    ed = sub.add_parser(
        "encode-dir",
        help="Encode all files in a directory",
        description=(
            "Recursively encode all non-.glyph files in a directory.\n\n"
            "Existing .glyph files are skipped.\n"
            "Password and recovery settings apply to all encoded files."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ed.add_argument("path", help="Path to the directory to encode")
    ed.add_argument(
        "--lock",
        action="store_true",
        help="Protect encoded files with a password",
    )
    ed.add_argument(
        "--recovery",
        action="store_true",
        help="Generate a one-time recovery key (displayed once)",
    )
    ed.add_argument(
        "--plan",
        action="store_true",
        help="Show what would be encoded without modifying any files",
    )

    dd = sub.add_parser(
        "decode-dir",
        help="Decode all .glyph files in a directory",
        description=(
            "Recursively decode all .glyph files in a directory.\n\n"
            "You will be prompted for a password only if at least one file is locked.\n"
            "A successful unlock applies to the entire directory session."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    dd.add_argument("path", help="Path to the directory to decode")
    dd.add_argument(
        "--plan",
        action="store_true",
        help="Show what would be decoded without modifying any files",
    )
    args = parser.parse_args()
    engine = GlyphLockEngine()

    try:
        if args.cmd == "encode":
            if args.path.endswith(".glyph"):
                raise GlyphLockError("already a glyph file")
            if os.path.isdir(args.path):
                raise GlyphLockError(
                    "you cannot encode a directory, please use encode-dir"
                )
            out = os.path.splitext(args.path)[0] + ".glyph"
            if args.plan:
                print(f"PLAN encode  {args.path} → {out}")
                return
            password = None
            if args.lock:
                password = getpass.getpass("Password: ")
            recovery_info = None
            if args.recovery:
                recovery_info, token = engine.security.create_recovery()
                print("\nRecovery key (store safely, shown once):")
                print(token)
                print()
            engine.encode_file(
                args.path,
                password=password,
                recovery=recovery_info,
            )

        elif args.cmd == "encode-dir":
            files = [
                p for p in engine.walker.iter_files(args.path)
                if not p.endswith(".glyph")
            ]
            if args.plan:
                for p in files:
                    out = os.path.splitext(p)[0] + ".glyph"
                    print(f"PLAN encode  {p} → {out}")
                return
            password = None
            if args.lock:
                password = getpass.getpass("Password: ")
            recovery_info = None
            if args.recovery:
                recovery_info, token = engine.security.create_recovery()
                print("\nRecovery key (store safely, shown once):")
                print(token)
                print()
            for p in files:
                engine.encode_file(
                    p,
                    password=password,
                    recovery=recovery_info,
                )

        elif args.cmd == "decode":
            if not args.path.endswith(".glyph"):
                raise GlyphLockError("not a glyph file")
            out = args.path[:-6]
            if args.plan:
                print(f"PLAN decode  {args.path} → {out}")
                return
            password = None
            header = peek_header(engine, args.path)
            if header.lock is not None:
                password = getpass.getpass("Password: ")
                if not password:
                    password = None
            engine.decode_file(args.path, password=password)

        elif args.cmd == "decode-dir":
            files = [
                p for p in engine.walker.iter_files(args.path)
                if p.endswith(".glyph")
            ]
            if args.plan:
                for p in files:
                    print(f"PLAN decode  {p}")
                return
            needs_password = False
            for p in files:
                header = peek_header(engine, p)
                if header.lock is not None:
                    needs_password = True
                    break
            password = None
            if needs_password:
                password = getpass.getpass("Password: ")
                if not password:
                    password = None
            had_errors = False
            for p in files:
                try:
                    engine.decode_file(p, password=password)
                except GlyphLockError as e:
                    had_errors = True
                    sys.stderr.write(f"{p}: {e}\n")
            if had_errors:
                sys.exit(1)

    except GlyphLockError as e:
        sys.stderr.write(f"glyphlock error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

