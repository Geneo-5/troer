#!/usr/bin/env python3
from sys import exit, stderr
from os import EX_OK, EX_DATAERR, EX_IOERR, EX_USAGE
from argparse import ArgumentParser
from subprocess import run
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

#--align-with-spaces:	 	Indentation
#--blank-after-sizeof:	 	Statements
#--blank-lines-after-commas:	 	Declarations
#--blank-lines-after-declarations:	 	-bad
#--blank-lines-after-procedures:	 	-bap
#--blank-lines-before-block-comments:	 	Blank lines
#--brace-indentn:	 	Statements
#--braces-after-func-def-line:	 	Declarations
#--braces-after-if-line:	 	Statements
#--braces-after-struct-decl-line:	 	Declarations
#--braces-on-func-def-line:	 	Declarations
#--braces-on-if-line:	 	Statements
#--braces-on-struct-decl-line:	 	Declarations
#--break-after-boolean-operator:	 	Breaking long lines
#--break-before-boolean-operator:	 	Breaking long lines
#--break-function-decl-args:	 	Declarations
#--break-function-decl-args-end:	 	Declarations
#--case-brace-indentationn:	 	Statements
#--case-indentationn:	 	Statements
#--comment-delimiters-on-blank-lines:	 	Comments
#--comment-indentationn:	 	Comments
#--continuation-indentationn:	 	Indentation
#--continue-at-parentheses:	 	Indentation
#--cuddle-do-while:	 	Statements
#--cuddle-else:	 	Statements
#--declaration-comment-columnn:	 	Comments
#--declaration-indentationn:	 	Declarations
#--dont-break-function-decl-args:	 	Declarations
#--dont-break-function-decl-args-end:	 	Declarations
#--dont-break-procedure-type:	 	Declarations
#--dont-cuddle-do-while:	 	Statements
#--dont-cuddle-else:	 	Statements
#--dont-format-comments:	 	Comments
#--dont-format-first-column-comments:	 	Comments
#--dont-left-justify-declarations:	 	Comments
#--dont-line-up-parentheses:	 	Indentation
#--dont-space-special-semicolon:	 	Statements
#--dont-star-comments:	 	Comments
#--dont-tab-align-comments:	 	Comments
#--else-endif-columnn:	 	Comments
#--fix-nested-comments:	 	Comments
#--format-all-comments:	 	Comments
#--format-first-column-comments:	 	Comments
#--gettext-strings:	 	Breaking long lines
#--gettext-strings:	 	Breaking long lines
#--gnu-style:	 	Common styles
#--honour-newlines:	 	Breaking long lines
#--ignore-newlines:	 	Breaking long lines
#--ignore-profile:	 	Invoking indent
#--indent-labeln:	 	Indentation
#--indent-leveln:	 	Indentation
#--k-and-r-style:	 	Common styles
#--leave-optional-blank-lines:	 	Blank lines
#--leave-preprocessor-space:	 	Indentation
#--left-justify-declarations:	 	Comments
#--line-comments-indentationn:	 	Comments
#--line-lengthn:	 	Breaking long lines
#--linux-style:	 	Common styles
#--no-blank-lines-after-commas:	 	Declarations
#--no-blank-lines-after-declarations:	 	-bad
#--no-blank-lines-after-procedures:	 	-bap
#--no-blank-lines-before-block-comments:	 	Blank lines
#--no-comment-delimiters-on-blank-lines:	 	Comments
#--no-parameter-indentation:	 	Indentation
#--no-space-after-cast:	 	Statements
#--no-space-after-for:	 	Statements
#--no-space-after-function-call-names:	 	Statements
#--no-space-after-if:	 	Statements
#--no-space-after-while:	 	Statements
#--no-tabs:	 	Declarations
#--no-tabs:	 	Indentation
#--no-verbosity:	 	Miscellaneous options
#--original:	 	Common styles
#--output-file:	 	Invoking indent
#--parameter-indentationn:	 	Indentation
#--preprocessor-indentationn:	 	Indentation
#--preserve-mtime:	 	Miscellaneous options
#--procnames-start-lines:	 	Declarations
#--remove-preprocessor-space:	 	Indentation
#--single-line-conditionals:	 	Statements
#--space-after-cast:	 	Statements
#--space-after-for:	 	Statements
#--space-after-if:	 	Statements
#--space-after-parentheses:	 	Statements
#--space-after-procedure-calls:	 	Statements
#--space-after-while:	 	Statements
#--space-special-semicolon:	 	Statements
#--spaces-around-initializers:	 	Declarations
#--standard-output:	 	Invoking indent
#--star-left-side-of-comments:	 	Comments
#--swallow-optional-blank-lines:	 	Blank lines
#--tab-sizen:	 	Indentation
#--use-tabs:	 	Declarations

def build_mode(parsed, mode, out_file, cmp_out, indent_profile):
    out = parsed.rendering(mode)
    if indent_profile:
        indent = ["env", f"INDENT_PROFILE={indent_profile}", "indent", "--standard-output"]
    else:
        indent = ["indent",
                  "--standard-output",
                  "--ignore-profile",
                  "-as",
                  "-nbad",
                  "-bap",
                  "-nbc",
                  "-bbo",
#                  "-hnl",
                  "-br",
                  "-brs",
                  "-c0",
                  "-cd0",
                  "-ncdb",
                  "-ce",
                  "-ci4",
                  "-cli0",
                  "-d0",
                  "-di1",
                  "-nfc1",
                  "-i8",
                  "-ip0",
                  "-l80",
                  "-lp",
                  "-npcs",
                  "-nprs",
                  "-npsl",
                  "-sai",
                  "-saf",
                  "-saw",
                  "-ncs",
                  "-sc",
                  "-sob",
                  "-fc1",
                  "--ignore-newlines",
                  "-cp0",
                  "-ss",
                  "-ts8",
                  "-il1" ]

    out = run(indent, capture_output=True, input=str(out), encoding="utf-8")
    if out.returncode != 0:
        raise Exception(out.stderr)
    out = out.stdout

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

