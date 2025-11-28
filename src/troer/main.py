#!/usr/bin/env python3
from sys import exit, stderr
from os import EX_OK, EX_DATAERR, EX_IOERR, EX_USAGE
from argparse import ArgumentParser, BooleanOptionalAction
from subprocess import run
from .elem import loadTroer
from .makefile import Makefile
from re import sub
from traceback import print_exc

def indent(data):
    indent = ["indent",
              "--standard-output",
              "--ignore-profile",
              "-linux",
              "--align-with-spaces",
              "--else-endif-column0"
    ]
    out = run(indent, capture_output=True, input=str(data), encoding="utf-8")
    if out.returncode != 0:
        raise Exception(out.stderr)
    out = out.stdout
    out = sub('[ \t\r\f\v]+\n', '\n', out) # remove all white space before end of line
    out = sub('\n+\n', '\n\n', out)   # remove all multiple empty line
    return out

def cli():
    parser = ArgumentParser(description='IDL translatore to dpack serializer')
    parser.add_argument('spec', type=str)
    parser.add_argument('outputDir', type=str,
            help='Save files generated in Output directory.')
    parser.add_argument('-I', '--include', dest='includeDir', type=str, 
            action='append', default=['.'],
            help='Path to include directory. Can add multiple time.')
    parser.add_argument('-j', '--json', action=BooleanOptionalAction,
            default=False, help='add json to/from dpack encoder/decoder')
    parser.add_argument('-m', '--makefile', default='no',
            choices=['no', 'builtin', 'static', 'shared', 'both'],
            help='Create ebuild makefile')
    parser.add_argument('--indent', action=BooleanOptionalAction,
            default=True, help='Use indent for rendering.')
    parser.add_argument('--include-prefix', type=str, dest='include_prefix',
            default=None, help='Path to directory to write include file')
    parser.add_argument('--include-dir', type=str, dest='include_dir',
            default=None, help='Path to directory to write include file')
    args = parser.parse_args()
    try:
        troer = loadTroer(args.spec, args)
        if args.makefile != 'no':
            makefile = Makefile(troer, args.makefile)
            makefile.rendering(args.outputDir)
        troer.rendering(args.outputDir, indent if args.indent else None)
    except Exception:
        print_exc()
        return EX_IOERR
    return EX_OK

if __name__ == "__main__":
    exit(cli())

