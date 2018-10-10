#!/usr/bin/env python3

import icq, sculptor
import numpy as np

cubeicq = './shapes/cube2.icq'

def render(sculptor, filename, theta=3*np.pi/8, phi=np.pi/5):
	sculptor.renderShape(filename, cameraR=100., cameraTheta=theta, cameraPhi=phi,
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
upscaleMargin = 8
scu.upscaleShape()
scu.rollIntoABall(radius=15.)
scu.perturbWithSphericalHarmonic(10., 2, 3, upscaleMargin=upscaleMargin)
render(scu, 'perturbed23.png')
scu.rollIntoABall(radius=15.)
scu.perturbWithSphericalHarmonic(10., 3, 4, upscaleMargin=upscaleMargin)
render(scu, 'perturbed34.png')
scu.rollIntoABall(radius=15.)
scu.perturbWithSphericalHarmonic(10., -4, 4, upscaleMargin=upscaleMargin)
render(scu, 'perturbed-44.png')
scu.rollIntoABall(radius=15.)
scu.perturbWithSphericalHarmonic(2., 11, 19, upscaleMargin=upscaleMargin)
render(scu, 'perturbed67.png')
