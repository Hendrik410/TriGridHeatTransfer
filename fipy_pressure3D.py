from fipy import Gmsh3D, FaceVariable, CellVariable, Viewer, DiffusionTerm
import math
import numpy as np

from materials import SiC, Nitrogen

# Simulationsvorgaben ---------------------------------------------------------

# Das anzunehmnde Material
material = SiC

# Das stroemende Fluid
fluid = Nitrogen

sweeps = 50

# [bar] Druck an der aeusseren Kante
Pamb = 0.96
# [bar] Druck an der inneren Kante
Pres = 2.25
# [bar] Druck in jeder Zelle zu Begin der Berechnungen
P0 = (Pamb + Pres) / 2.0

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

Dx = material["k_x"] * fluid["dichte"]
Dy = material["k_y"] * fluid["dichte"]
Dz = material["k_y"] * fluid["dichte"]


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

phi = CellVariable(name = "Pressure", mesh = mesh, value = P0)


D = FaceVariable(mesh=mesh, value=((Dx,0,0), 
                                   (0,Dy,0),
                                   (0,0,Dz)))

# boundry conditions ----------------------------------------------------------

phi.constrain(Pres, where=mesh.physicalFaces["inner"])
phi.constrain(Pamb, where=mesh.physicalFaces["outer"])


# Solving ---------------------------------------------------------------------


eq = DiffusionTerm(coeff=D)
sweep = 0

phi_old = phi.copy()

max_diff = 10e10

#while True:
for sweep in range(sweeps):
#while max_diff > 10e-6:
    print "Doing sweep {} | max_diff: {}".format(sweep, max_diff)
    res = eq.sweep(var=phi)
    print "Residual: {}".format(res)
    
    new_max_diff = np.absolute(phi_old.value - phi.value).max() 
    phi_old = phi.copy()
    
    pressureFaces = phi.arithmeticFaceValue
    D[0,0,:] = material["k_x"] * pressureFaces[:]
    D[1,1,:] = material["k_y"] * pressureFaces[:]
    D[2,2,:] = material["k_y"] * pressureFaces[:]
    
    
    sweep = sweep + 1
    max_diff = new_max_diff


viewer = Viewer(vars=phi, datamin=Pamb*0.9, datamax=Pres*1.1)
viewer.plot()

#===============================================================================
# viewer = Viewer(vars=phi, datamin=Pamb*0.9, datamax=Pres*1.1)
# 
# print "Calculation started"
# started = time.clock()
# 
# DiffusionTerm(coeff=D).solve(var=phi)
# 
# print "Calculation finished, took {} seconds".format(time.clock() - started)
# 
# viewer.plot()
# 
# raw_input("Press enter to close ...")
#===============================================================================

