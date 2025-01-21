#!/usr/bin/env python3
from sys import exit, stderr
from os import EX_OK, EX_DATAERR, EX_IOERR, EX_USAGE
from argparse import ArgumentParser
from subprocess import run
from .spec import *
from re import sub

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

INDENT_CMD = [ "-linux",
# Indentation
    "--align-with-spaces",
#    "--continuation-indentationn",
#    "--continue-at-parentheses",
#    "--dont-line-up-parentheses",
#    "--indent-label0",
#    "--indent-leveln",
#    "--leave-preprocessor-space",
#    "--no-parameter-indentation",
#    "--parameter-indentationn",
#    "--preprocessor-indentation1",
#    "--remove-preprocessor-space",
#    "--tab-size8",
#
# Statements
#    "--blank-after-sizeof",
#    "--brace-indent0",
#    "--braces-after-if-line",
#    "--braces-on-if-line",
#    "--case-brace-indentation0",
#    "--case-indentation0",
#    "--cuddle-do-while",
#    "--cuddle-else",
#    "--dont-cuddle-do-while",
#    "--dont-cuddle-else",
#    "--dont-space-special-semicolon",
#    "--no-space-after-cast",
#    "--no-space-after-for",
#    "--no-space-after-function-call-names",
#    "--no-space-after-if",
#    "--no-space-after-while",
#    "--single-line-conditionals",
#    "--space-after-cast",
#    "--space-after-for",
#    "--space-after-if",
#    "--space-after-parentheses",
#    "--space-after-procedure-calls",
#    "--space-after-while",
#    "--space-special-semicolon",
#
# Declarations
#    "--blank-lines-after-commas",
#    "--braces-after-func-def-line",
#    "--braces-after-struct-decl-line",
#    "--braces-on-func-def-line",
#    "--braces-on-struct-decl-line",
#    "--break-function-decl-args",
#    "--break-function-decl-args-end",
#    "--declaration-indentation16",
#    "--dont-break-function-decl-args",
#    "--dont-break-function-decl-args-end",
#    "--dont-break-procedure-type",
#    "--no-blank-lines-after-commas",
#    "--no-tabs",
#    "--use-tabs",
#    "--procnames-start-lines",
#    "--spaces-around-initializers",
#
# Blank lines
#    "--blank-lines-before-block-comments",
#    "--no-blank-lines-before-block-comments",
#    "--leave-optional-blank-lines",
#    "--swallow-optional-blank-lines",
#    "--blank-lines-after-procedures",
#    "--no-blank-lines-after-procedures",
#    "--blank-lines-after-declarations",
#    "--no-blank-lines-after-declarations",
#
# Breaking long lines
#    "--break-after-boolean-operator",
#    "--break-before-boolean-operator",
#    "--gettext-strings",
#    "--ignore-newlines",
#    "--honour-newlines",
#    "--line-length80",
#
# Comments
#    "--comment-delimiters-on-blank-lines",
#    "--no-comment-delimiters-on-blank-lines",
#    "-blank-lines-before-block-comments",
#    "--comment-indentation0",
#    "--declaration-comment-column0",
#    "--line-comments-indentation0",
#    "--dont-format-comments",
#    "--dont-star-comments",
#    "--dont-tab-align-comments",
    "--else-endif-column0",
#    "--fix-nested-comments",
#    "--format-all-comments",
#    "--format-first-column-comments",
#    "--dont-format-first-column-comments",
#    "--left-justify-declarations",
#    "--dont-left-justify-declarations",
#    "-sc", # "--star-left-side-of-comments",
#    "--comment-line-length80",
]

def build_mode(parsed, mode, out_file, cmp_out, indent_profile):
    out = parsed.rendering(mode)
    if indent_profile:
        indent = ["env", f"INDENT_PROFILE={indent_profile}",
                "indent", "--standard-output"]
    else:
        indent = ["indent", "--standard-output", "--ignore-profile"] + \
                INDENT_CMD
    out = run(indent, capture_output=True, input=str(out), encoding="utf-8")
    if out.returncode != 0:
        raise Exception(out.stderr)
    out = out.stdout
    out = sub('[ \t\r\f\v]+\n', '\n', out) # remove all white space before end of line
    out = sub('\n+\n', '\n\n', out)   # remove all multiple empty line

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
    parser.add_argument('--profile', dest='profile', type=str, default=None,
            help = 'Path to indent profile file')
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
            build_mode(parsed, args.mode, args.out_file, args.cmp_out,
                    args.profile)
        elif args.all:
            for m in modes[parsed.schema]:
                f = None
                if args.out_file:
                    prefix, ext = mode_files[m]
                    f = f"{args.out_file}/{prefix}{parsed.name}.{ext}"
                build_mode(parsed, m, f, args.cmp_out, args.profile)
    except Exception as e:
        print(e)
        return EX_IOERR

    return EX_OK

if __name__ == "__main__":
    exit(cli())

