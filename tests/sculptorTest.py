#!/usr/bin/env python3

import icq, sculptor
import numpy as np

cubeicq = './shapes/cube2.icq'

def render(sculptor, filename, theta=3*np.pi/8, phi=np.pi/5):
	sculptor.renderShape(filename, cameraR=150., cameraTheta=theta, cameraPhi=phi,
                                 lightR=100., lightTheta=np.pi/4, lightPhi=np.pi/2,
	                               lightColor=(2,2,2), objectColor=(0.5,0.5,1.5))

# Reading the initial cube and rolling it into a sphere
ish = icq.ICQShape()
ish.readICQ(cubeicq)

scu = sculptor.Sculptor(ish)
scu.rollIntoABall(radius=15.)

# Rendering the initial sphere
render(scu, 'blank.png')

# Upscaling it and rolling again
scu.upscaleShape()
scu.rollIntoABall(radius=15.)
render(scu, 'blank-hr.png')

# Adding spherical harmonics to it
scu.upscaleShape()
scu.rollIntoABall(radius=15.)
scu.perturbWithSphericalHarmonic(10., 3, 5)
render(scu, 'perturbed.png')
