#!/usr/bin/env python3

import icq
import numpy as np

cubeicq = './shapes/cube4.icq'
outfile = 'cube.png'

ish = icq.ICQShape()
print('Rendering {} to {}'.format(cubeicq, outfile))
ish.readICQ(cubeicq)
ish.renderSceneSpherical(outfile, cameraR=200., cameraTheta=3*np.pi/8, cameraPhi=np.pi/5,
                                  lightR=100., lightTheta=np.pi/4, lightPhi=np.pi/2,
	                                lightColor=(2,2,2), objectColor=(0.5,0.5,1.5))
