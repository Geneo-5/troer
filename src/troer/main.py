#!/usr/bin/env python3
from sys import exit, stderr
from os import EX_OK, EX_DATAERR, EX_IOERR, EX_USAGE
from argparse import ArgumentParser
from .spec import *

modes = {
    "storage": [
        "lib-header",
        "lib-src",
        # "json-header"
        # "json-src"
    ],
    "exchange" : [
        "lib-header",
        "lib-src",
        "json-header"
        "json-src",
        "user-header",
        "user-src",
        "server-header",
        "server-src"
    ]
}


mode_files = {
    "lib-header":    {"", ".h"},
    "lib-src":       {"", ".c"},
    "json-header":   {"json-", ".h"},
    "json-src":      {"json-", ".c"},
    "user-header":   {"user-", ".h"},
    "user-src":      {"user-", ".c"},
    "server-header": {"srv-", ".h"},
    "server-src":    {"srv-", ".c"},
}

def build_mode(parsed, mode, out_file, cmp_out):
    out = parsed.rendering(mode)

    if not out_file:
        print(out)
        return

    if cmp_out:
        try:
            with open(out_file, 'r') as f:
                data = f.read()
            if data == out:
                return
        except:
            pass

        with open(out_file, 'w') as f:
            f.write(out)

def cli():
    parser = ArgumentParser(description='IDL translatore to dpack serializer')
    parser.add_argument('--spec', dest='spec', type=str, required=True)
    parser.add_argument('--mode', dest='mode', type=str, default=None)
    parser.add_argument('--all', action='store_true', default=None, help='Build all modes')
    parser.add_argument('--cmp-out', action='store_true', default=None,
        help='Do not overwrite the output file if the new output is identical to the old')
    parser.add_argument('-o', dest='out_file', type=str, default=None)
    args = parser.parse_args()

    if (args.all and  args.mode) or not (args.all or  args.mode):
        print("Choice --all xor --mode MODE", file=stderr)
        return EX_USAGE

    try:
        parsed = SpecFamily(args.spec)

        if args.mode and args.mode not in modes[parsed.schema]:
            print(f"Bad mode {args.mode} must be in [{modes[parsed.schema]}]", file=stderr)
            return EX_USAGE

        if args.mode:
            build_mode(parsed, args.mode, args.out_file, args.cmp_out)
        elif args.all:
            for m in modes[parsed.schema]:
                f = None
                if args.out_file:
                    prefix, ext = mode_files[m]
                    f = f"{args.out_file}/{prefix}{parsed.name}.{ext}"
                build_mode(parsed, m, f, args.cmp_out)
    except Exception as e:
        print(e)
        return EX_IOERR

    return EX_OK

if __name__ == "__main__":
    exit(cli())

