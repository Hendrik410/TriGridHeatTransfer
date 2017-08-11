from fipy import CellVariable, Gmsh2D, DiffusionTerm, Viewer, Variable, TransientTerm
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

# D kann einfache Variable sein, da sie Ortsunabhängig ist
D = Variable(value=((Dx,0), 
                    (0,Dy)))



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


#mesh = Gmsh2D("C:\\Users\\muel_hd\\Desktop\\test.geo") 
mesh = Gmsh2D(geometryTemplate) 


phi = CellVariable(name = "Temperature", mesh = mesh, value = T0)


# Die Waermeleitungsgleichung
equation = TransientTerm() == DiffusionTerm(coeff=D)





# boundry conditions ----------------------------------------------------------


phi.constrain(Ti, where=mesh.physicalFaces["inner"])
phi.constrain(Te, where=mesh.physicalFaces["outer"])

# Viewer mit Limits entsprechend den Werten initialisieren
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
            viewer.plot() # Interactive plot
         
         
raw_input("Press enter to close ...")

