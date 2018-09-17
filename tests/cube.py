#!/usr/bin/env python3

import icq

ish = icq.ICQShape()
ish.readICQ('./shapes/cube4.icq')
scn = ish.getScene(cameraLocation=[100,100,40], lightColor=[2,2,2], lightLocation=[50,100,20], objectColor=[0.5,0.5,1.5])
scn.render('cube.png', height=1024, width=1024, antialiasing=0.001)
