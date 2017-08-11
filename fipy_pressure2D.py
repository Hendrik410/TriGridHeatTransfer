from fipy import CellVariable, FaceVariable, Gmsh2D, DiffusionTerm, Matplotlib2DViewer, MatplotlibVectorViewer
import numpy as np
import math

from materials import SiC, Nitrogen

# Simulationsvorgaben ---------------------------------------------------------

# Das anzunehmnde Material
material = SiC

# Das stroemende Fluid
fluid = Nitrogen

# [kg/sm^2] Massenstrom 
massflow = 2.0

sweeps = 200

# [bar] Druck an der aeusseren Kante
Pamb = 0.96
# [bar] Druck an der inneren Kante
Pres = 2.25
# [bar] Druck in jeder Zelle zu Begin der Berechnungen
P0 = (Pamb + Pres) / 2.0

# [m] Groesse der Zellen
cellSize = 0.001

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

Physical Line("outer") = {{14}};
Physical Line("inner") = {{11, 12}};
Physical Surface("surface") = {{16}};

'''.format(
    cellSize,
    l1,
    l2,
    math.tan(beta) * (l2 - l1),
    l3,
    math.tan(alpha) * l3)


mesh = Gmsh2D(geometryTemplate) 

phi = CellVariable(name = "Pressure", mesh = mesh, value = P0)

Dx = material["k_x"] * fluid["dichte"]
Dy = material["k_y"] * fluid["dichte"]

# D muss eine Face Variable sein, da der Koeffizient für jede Flaeche unterschiedlich ist
D = FaceVariable(mesh=mesh, value=((Dx,0), 
                                   (0,Dy)))

# boundry conditions ----------------------------------------------------------

phi.constrain(Pres, where=mesh.physicalFaces["inner"])
phi.constrain(Pamb, where=mesh.physicalFaces["outer"])


# Solving ---------------------------------------------------------------------


eq = DiffusionTerm(coeff=D)
sweep = 0

phi_old = phi.copy()

max_diff = 10e10

#while True:
#for sweep in range(sweeps):
while max_diff > 10e-3:
    # sweep berechnen
    print "Doing sweep {} | max_diff: {}".format(sweep, max_diff)
    eq.sweep(var=phi)
    
    # maximale Differnz zwischen Zellen berechnen
    new_max_diff = np.absolute(phi_old.value - phi.value).max() 
    phi_old = phi.copy()
    
    # Koeffizienten neu berechnen
    pressureFaces = phi.arithmeticFaceValue
    D[0,0,:] = material["k_x"] * pressureFaces[:]
    D[1,1,:] = material["k_y"] * pressureFaces[:]
    
    
    sweep = sweep + 1
    #if new_max_diff - max:
    #    break;
    max_diff = new_max_diff
    

# Gradienten über das Gitter umrechnen in Massenstroeme
grad = phi.faceGrad

grad[0,:] = grad[0,:] * -material["k_x"] * fluid["dichte"] / fluid["viscosity"]
grad[1,:] = grad[1,:] * -material["k_y"] * fluid["dichte"] / fluid["viscosity"]

total_sum = np.sqrt(grad[0,:]**2 + grad[1,:]**2).sum()
grad = grad * (massflow/total_sum)


# Viewer für das mesh zuerst erstellen
viewer = Matplotlib2DViewer(vars=phi, datamin=Pamb*0.9, datamax=Pres*1.1)

# Pfeile für Massenstrom auf die selbe Flaeche zeichnen
grad_viewer = MatplotlibVectorViewer(vars=grad, axes=viewer.axes, title="Pressure & Massflow", scale=.1)
grad_viewer.plot()

# Mesh zeichnen und gesamtes Bild abspeichern
viewer.plot(filename="results/{}_{}_{}.png".format(cellSize, sweep + 1, massflow))

#raw_input("Press enter to close ...")

