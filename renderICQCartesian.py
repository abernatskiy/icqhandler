#!/usr/bin/env python3

renderWidth = 500
renderHeight = 500
brightness = 5

import argparse

parser = argparse.ArgumentParser(description='Convert a 3d shape in .ICQ format into Wavefront .OBJ format')
parser.add_argument('icqFileName', metavar='icqFileName', type=str)
parser.add_argument('camX', metavar='camX', type=float)
parser.add_argument('camY', metavar='camY', type=float)
parser.add_argument('camZ', metavar='camZ', type=float)
parser.add_argument('pngFileName', metavar='pngFileName', type=str, nargs='?')
parser.add_argument('phase', metavar='phase', type=float, nargs='?')

cliArgs = parser.parse_args()
icqFileName = cliArgs.icqFileName
camX = cliArgs.camX
camY = cliArgs.camY
camZ = cliArgs.camZ
pngFileName = cliArgs.icqFileName[:-4] + '_x{}_y{}_z{}.png'.format(camX, camY, camZ) if cliArgs.pngFileName is None else cliArgs.pngFileName
phase = cliArgs.phase

print('Rendering shape model {} to {}'.format(icqFileName, pngFileName))

import icq
ish = icq.ICQShape()
ish.readICQ(icqFileName)
if not ish.validate(exceptionIfInvalid=False):
	print('WARNING: input ICQ file {} is invalid!'.format(icqFileName))

ish.renderSceneCartesian(pngFileName, cameraLocation=[camX, camY, camZ],
#                                      rotationAxis=astRotAxis, rotationAngle=ph,
                                      lightLocation=[camX, camY, camZ], lightColor=[brightness, brightness, brightness],
                                      backgroundColor=(0,0,0), objectColor=[0.5,0.5,0.5],
                                      width=renderWidth, height=renderHeight,
                                      rotationAxis=(-1,1,-1), rotationAngle=phase*6.28/75.,
                                      antialiasing=0.01)
