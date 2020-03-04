#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description='Convert a 3d shape in .ICQ format into Wavefront .OBJ format')
parser.add_argument('icqFileName', metavar='icqFileName', type=str)
parser.add_argument('objFileName', metavar='objFileName', type=str, nargs='?')

cliArgs = parser.parse_args()
icqFileName = cliArgs.icqFileName
objFileName = cliArgs.icqFileName[:-4] + '.obj' if cliArgs.objFileName is None else cliArgs.objFileName

import icq

ish = icq.ICQShape()
ish.readICQ(icqFileName)
if not ish.validate(exceptionIfInvalid=False):
	print('WARNING: input ICQ file {} is invalid!'.format(icqFileName))
ish.writeOBJ(objFileName)
