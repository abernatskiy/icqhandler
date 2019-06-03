#!/usr/bin/env python3

renderWidth = 500
renderHeight = 500
brightness = 5

import argparse

parser = argparse.ArgumentParser(description='Render a shape in ICQ format')
parser.add_argument('icqFileName', metavar='icqFileName', type=str)
parser.add_argument('camR', metavar='camR', type=float)
parser.add_argument('camT', metavar='camT', type=float)
parser.add_argument('camP', metavar='camP', type=float)
parser.add_argument('pngFileName', metavar='pngFileName', type=str, nargs='?')

cliArgs = parser.parse_args()
icqFileName = cliArgs.icqFileName
camR = cliArgs.camR
camT = cliArgs.camT
camP = cliArgs.camP
pngFileName = cliArgs.icqFileName[:-4] + '_r{}_t{}_p{}.png'.format(camR, camT, camP) if cliArgs.pngFileName is None else cliArgs.pngFileName

print('Rendering shape model {} to {}'.format(icqFileName, pngFileName))

import icq
ish = icq.ICQShape()
ish.readICQ(icqFileName)
if not ish.validate(exceptionIfInvalid=False):
	print('WARNING: input ICQ file {} is invalid!'.format(icqFileName))

ish.renderSceneCartesian(pngFileName, cameraR=camR, cameraTheta=camT, cameraPhi=camP,
#                                      rotationAxis=astRotAxis, rotationAngle=ph,
                                      lightR=camR, lightT=camT, lightP=camP,
                                      lightColor=[brightness, brightness, brightness],
                                      backgroundColor=(0,0,0), objectColor=[0.5,0.5,0.5],
                                      width=renderWidth, height=renderHeight,
                                      antialiasing=0.01)
