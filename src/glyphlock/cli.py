#glyphlock/cli.py
import argparse
import getpass
import os
import sys

from .operations import GlyphLockEngine
from .errors import GlyphLockError


def main():
    parser = argparse.ArgumentParser("glyphlock")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ef = sub.add_parser("encode")
    ef.add_argument("path")
    ef.add_argument("--lock", action="store_true")
    ef.add_argument("--recovery", action="store_true")
    ef.add_argument("--plan", action="store_true")

    df = sub.add_parser("decode")
    df.add_argument("path")
    df.add_argument("--plan", action="store_true")

    ed = sub.add_parser("encode-dir")
    ed.add_argument("path")
    ed.add_argument("--lock", action="store_true")
    ed.add_argument("--recovery", action="store_true")
    ed.add_argument("--plan", action="store_true")

    dd = sub.add_parser("decode-dir")
    dd.add_argument("path")
    dd.add_argument("--plan", action="store_true")

    args = parser.parse_args()
    engine = GlyphLockEngine()

    try:
        if args.cmd == "encode":
            if args.path.endswith(".glyph"):
                raise GlyphLockError("already a glyph file")
            if os.path.isdir(args.path):
                raise GlyphLockError("you cannot encode a directory, please use a file")
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
            engine.decode_file(args.path, password=None)

        elif args.cmd == "decode-dir":
            files = [
                p for p in engine.walker.iter_files(args.path)
                if p.endswith(".glyph")
            ]
            if args.plan:
                for p in files:
                    print(f"PLAN decode  {p}")
                return
            had_errors = False
            for p in files:
                try:
                    engine.decode_file(p, password=None)
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

