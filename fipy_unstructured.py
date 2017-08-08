'''
Created on 07.08.2017

@author: muel_hd
'''

from fipy import *
import numpy as np
import math

from materials import Aluminum, SiC

# Simulationsvorgaben ---------------------------------------------------------

# Das anzunehmnde Material
material = SiC

# [s] Der Zeitschritt der Simulation 
dt = 0.01
# [s] Die Gesamtzeit der Simulation
total_time = 20.0

# [K] Temperatur jeder Zelle zu Begin der Berechnungen
T0 = 50.0
# [K] Temperatur an der aeusseren Kante
Te = 1200.0
# [K] Temperatur an der inneren Kante
Ti = 200.0


# [m] Groesse der Zellen
cellSize = 0.0005

# [m] Laenge 1
l1 = 16.13 / 1000.0
# [m] Laenge 2
l2 = 27.624 / 1000.0
# [m] Laenge 3
l3 = 31.784 / 1000.0

# [rad] Winkel der aeusseren Kante
alpha = math.radians(25.0)
# [rad] Winkel der inneren Kante
beta = math.radians(30.0)

# [bool] Wenn True, wird direkt das Gleichgewicht berechnet
steady_state=True

# Berechnete Werte ------------------------------------------------------------

# Anzahl der Zeitschritte
intervals = int(total_time / dt)

# Temperaturleitfaehigkeit in x und y Richtung in Tensor (D) zusammenfassen
Dx = material["lambda_x"] / (material["cp"] * material["dichte"])
Dy = material["lambda_y"] / (material["cp"] * material["dichte"])

D = Variable(value=((Dx,0), (0,Dy)))



# FiPy init -------------------------------------------------------------------


geometryTemplate = '''
cellSize = {0};

Point(1) = {{ 0,   0,   0,  cellSize}};
Point(2) = {{ {1}, 0,   0,  cellSize}};
Point(3) = {{ {2}, {3}, 0,  cellSize}};
Point(4) = {{ {4}, {3}, 0,  cellSize}};
Point(5) = {{ {4}, {5}, 0,  cellSize}};

Line(10) = {{1,2}};
Line(11) = {{2,3}};
Line(12) = {{3,4}};
Line(13) = {{4,5}};
Line(14) = {{5,1}};

Line Loop(15) = {{10,11,12,13,14}};
Plane Surface(16) = {{15}};'''.format(
    cellSize,
    l1,
    l2,
    math.tan(beta) * (l2 - l1),
    l3,
    math.tan(alpha) * l3)


#mesh = Gmsh2D("C:\\Users\\muel_hd\\Desktop\\test.geo") 
mesh = Gmsh2D(geometryTemplate) 


phi = CellVariable(name = "Temperature", mesh = mesh, value = T0)


# Die Waermeleitungsgleichung
equation = TransientTerm() == DiffusionTerm(coeff=D)





# boundry conditions ----------------------------------------------------------

def face_has_angle_sin(faceId, sin):
    return math.fabs(math.fabs(mesh.faceNormals[0,faceId]) - sin) < 0.001

def face_has_angle(faceId, angle):
    return face_has_angle_sin(faceId, math.sin(angle))

def is_exterior_face(faceId):
    return mesh.exteriorFaces[faceId]

def get_face_coordinates(faceId):
    return mesh.faceCenters.value[0, faceId], mesh.faceCenters.value[1, faceId]

def is_above_line(faceId, slope, offset):
    x,y = get_face_coordinates(faceId)
    return (slope * x) + offset < y

def is_below_line(faceId, slope, offset):
    x,y = get_face_coordinates(faceId)
    return (slope * x) + offset > y


tan_alpha = math.tan(alpha)
sin_alpha = math.sin(alpha)
sin_beta = math.sin(beta)

def is_upper_boundary(faceId):
    return is_exterior_face(faceId) and \
        face_has_angle_sin(faceId, sin_alpha) and \
        is_above_line(faceId, tan_alpha, -cellSize * 2)

def is_lower_boundary(faceId):
    return is_exterior_face(faceId) and is_below_line(faceId, tan_alpha, -cellSize*2) and \
        (face_has_angle_sin(faceId, sin_beta) or (face_has_angle(faceId, 0) and is_above_line(faceId, 0.0, 0.0)))



outerEdge = np.ndarray((mesh.numberOfFaces), dtype=bool)
innerEdge = np.ndarray((mesh.numberOfFaces), dtype=bool)

for i in range(mesh.numberOfFaces):
    outerEdge[i] = is_upper_boundary(i)
    
for i in range(mesh.numberOfFaces):
    innerEdge[i] = is_lower_boundary(i)


phi.constrain(Ti, innerEdge)
phi.constrain(Te, outerEdge)


viewer = Viewer(vars=phi, datamin=0., datamax=Te*1.1)


if steady_state:
    DiffusionTerm(coeff=D).solve(var=phi)

    viewer.plot()
else:
    viewer.plot()
    raw_input("Press enter to start the show")
    
    for i in range(intervals):
        equation.solve(var=phi, dt=dt)
        if __name__ == '__main__':
            viewer.plot()
         
         
raw_input("Press enter to close ...")

