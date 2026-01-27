#glyphlock/cli.py
import argparse
import sys

from .operations import GlyphLockEngine
from .errors import GlyphLockError


def main():
    parser = argparse.ArgumentParser("glyphlock")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("encode").add_argument("path")
    sub.add_parser("decode").add_argument("path")

    ed = sub.add_parser("encode-dir")
    ed.add_argument("path")
    ed.add_argument("--lock", action="store_true")
    ed.add_argument("--recovery", action="store_true")

    dd = sub.add_parser("decode-dir")
    dd.add_argument("path")

    args = parser.parse_args()
    engine = GlyphLockEngine()

    try:
        if args.cmd == "encode":
            engine.encode_file(args.path, None, False)
        elif args.cmd == "decode":
            engine.decode_file(args.path, None)
        elif args.cmd == "encode-dir":
            for p in engine.walker.iter_files(args.path):
                engine.encode_file(
                    p,
                    password=None if not args.lock else input("Password: "),
                    recovery=args.recovery,
                )
        elif args.cmd == "decode-dir":
            pw = input("Password: ")
            for p in engine.walker.iter_files(args.path):
                engine.decode_file(p, pw)
    except GlyphLockError as e:
        sys.stderr.write(f"glyphlock error: {e}\n")
        sys.exit(1)

