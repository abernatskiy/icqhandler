#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser(description='Convert a 3d shape in .ICQ format into Wavefront .OBJ format')
parser.add_argument('icqFileName', metavar='icqFileName', type=str)
parser.add_argument('camX', metavar='camX', type=float)
parser.add_argument('camY', metavar='camY', type=float)
parser.add_argument('camZ', metavar='camZ', type=float)
parser.add_argument('pngFileName', metavar='pngFileName', type=str, nargs='?')

cliArgs = parser.parse_args()
icqFileName = cliArgs.icqFileName
camX = cliArgs.camX
camY = cliArgs.camY
camZ = cliArgs.camZ
pngFileName = cliArgs.icqFileName[:-4] + '_x{}_y{}_z{}.png'.format(camX, camY, camZ) if cliArgs.pngFileName is None else cliArgs.pngFileName

print('Rendering shape model {} to {}'.format(icqFileName, pngFileName))

import icq
ish = icq.ICQShape()
ish.readICQ(icqFileName)
if not ish.validate(exceptionIfInvalid=False):
	print('WARNING: input ICQ file {} is invalid!'.format(icqFileName))

ish.renderSceneCartesian(pngFileName, cameraLocation=[camX, camY, camZ],
#                                      rotationAxis=astRotAxis, rotationAngle=ph,
                                      lightLocation=[camX, camY, camZ], lightColor=[1,1,1],
                                      backgroundColor=(0,0,0), objectColor=[0.5,0.5,0.5],
#                                      width=renderWidth, height=renderHeight,
                                      antialiasing=0.01)

