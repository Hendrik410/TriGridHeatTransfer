'''
Created on 07.08.2017

@author: muel_hd
'''
from fipy import *
import sys
import pylab

from materials import Aluminum, SiC




material = SiC


nx = 20
ny = nx
dx = .01
dy = dx
L = dx * nx
mesh = Grid2D(dx=dx, dy=dy, nx=nx, ny=ny)

phi = CellVariable(name = "solution variable",
                   mesh = mesh,
                   value = 0.)

Dx = material["lambda_x"] / (material["cp"] * material["dichte"])
Dy = material["lambda_y"] / (material["cp"] * material["dichte"])
I0 = Variable(value=((1,0), (0,0)))
I1 = Variable(value=((0,0), (0,1)))

D = Dx * I0 + Dy * I1
eq = TransientTerm() == DiffusionTerm(coeff=D)

valueTopLeft = 0
valueBottomRight = 1

X, Y = mesh.faceCenters
facesTopLeft = ((mesh.facesLeft & (Y > L / 2))
                | (mesh.facesTop & (X < L / 2)))
facesBottomRight = ((mesh.facesRight & (Y < L / 2))
                    | (mesh.facesBottom & (X > L / 2)))

phi.constrain(valueTopLeft, facesTopLeft)
phi.constrain(valueBottomRight, facesBottomRight)

if __name__ == '__main__':
    viewer = Viewer(vars=phi, datamin=0., datamax=1.)
    viewer.plot()
     
timeStepDuration = 5
steps = 100
for step in range(steps):
    eq.solve(var=phi, dt=timeStepDuration)
    if __name__ == '__main__':
        viewer.plot()

raw_input("Press enter...")