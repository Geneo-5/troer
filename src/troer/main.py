#!/usr/bin/env python3
from sys import exit
from os import EX_OK, EX_DATAERR, EX_IOERR
import argparse
from .spec import *

def cli():
	parser = argparse.ArgumentParser(description='IDL translatore to dpack serializer')
	parser.add_argument('--mode', dest='mode', type=str, required=True)
	parser.add_argument('--spec', dest='spec', type=str, required=True)
	parser.add_argument('--cmp-out', action='store_true', default=None,
		help='Do not overwrite the output file if the new output is identical to the old')
	parser.add_argument('-o', dest='out_file', type=str, default=None)
	args = parser.parse_args()
	try:
		parsed = SpecFamily(args.spec)
		out = parsed.rendering(args.mode)
	except Exception as e:
		print(e)
		return EX_DATAERR

	if not args.out_file:
		print(out)
		return EX_OK

	if args.cmp_out:
		try:
			with open(args.out_file, 'r') as f:
				data = f.read()
			if data == out:
				return EX_OK
		except:
			pass

	try:
		with open(args.out_file, 'w') as f:
			f.write(out)
	except Exception as e:
		print(e)
		return EX_IOERR

	return EX_OK

if __name__ == "__main__":
	exit(cli())
