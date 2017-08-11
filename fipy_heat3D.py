from fipy import Gmsh3D, Variable, CellVariable, Viewer, DiffusionTerm
import math
import time

from materials import Aluminum, SiC

# Simulationsvorgaben ---------------------------------------------------------

# Das anzunehmnde Material
material = SiC


# [K] Temperatur jeder Zelle zu Begin der Berechnungen
T0 = 500.0
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

# Berechnete Werte ------------------------------------------------------------

# Temperaturleitfaehigkeit in x und y Richtung in Tensor (D) zusammenfassen
Dx = material["lambda_x"] / (material["cp"] * material["dichte"])
Dy = material["lambda_y"] / (material["cp"] * material["dichte"])
Dz = material["lambda_y"] / (material["cp"] * material["dichte"])

# D als Urtsunabhängigen Tensor
D = Variable(value=((Dx,0,0), 
                    (0,Dy,0), 
                    (0,0,Dz)))



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
Plane Surface(16) = {{15}};

Extrude {{ {{1, 0, 0}}, {{0, 0, 0}}, Pi/2}} {{
  Surface{{16}}; 
}}

Physical Surface("inner") = {{30, 26}};
Physical Surface("outer") = {{37}};
Physical Volume("volume") = {{1}};

'''.format(
    cellSize,
    l1,
    l2,
    math.tan(beta) * (l2 - l1),
    l3,
    math.tan(alpha) * l3)


mesh = Gmsh3D(geometryTemplate) 

# Enthaelt die Temperatur
phi = CellVariable(name = "Temperature", mesh = mesh, value = T0)


# boundry conditions ----------------------------------------------------------


phi.constrain(Ti, where=mesh.physicalFaces["inner"])
phi.constrain(Te, where=mesh.physicalFaces["outer"])

# calculation -----------------------------------------------------------------

viewer = Viewer(vars=phi, datamin=200., datamax=Te*1.01)


print "Calculation started"
started = time.clock()

# Loest die Stationaere Waermegleichung
DiffusionTerm(coeff=D).solve(var=phi)

print "Calculation finished, took {} seconds".format(time.clock() - started)

viewer.plot()
         
raw_input("Press enter to close ...")

