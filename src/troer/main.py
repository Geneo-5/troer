#!/usr/bin/env python3
from sys import exit, stderr
from os import EX_OK, EX_DATAERR, EX_IOERR, EX_USAGE
from argparse import ArgumentParser
from subprocess import run
from .elem import loadTroer
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
    parser.add_argument('-o', dest='outputDir', type=str, default=None)
    parser.add_argument('-I', dest='includeDir', type=str, action='append',
            default=['.'])
    args = parser.parse_args()
    try:
        troer = loadTroer(args.spec, args.includeDir)
        troer.rendering(args.outputDir, indent)
    except Exception:
        print_exc()
        return EX_IOERR
    return EX_OK

if __name__ == "__main__":
    exit(cli())

