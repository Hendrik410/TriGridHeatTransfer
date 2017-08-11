import math
from time import clock
import numpy as np
import scipy.spatial as sp

from materials import SiC, Aluminum
from visualization import GridHistoryVisualization

# Punkte werden hier generiert
points = np.zeros((400, 2)) # x, y

for x in range(20):
    for y in range(20):
        points[x * 20 + y] = [x/4.0, y/4.0]


# generate points somehow

# Mesh aus Punkten erstellen mit Dalaunay Algo
tri = sp.Delaunay(points)
n_verts = tri.simplices.shape[0]

# Dieser Array enthaelt für jede Flaeche
#  Die x und y Koordinate des Mittelpunktes
#  Die drei Punkte, aus denen sie besteht
#  Die drei Nachbarzellen (-1 wenn kein Nachbar)
#  Die Flaeche in m^2
verts = np.zeros((n_verts, 9)) # x, y, p1, p2, p3, n1, n2, n3, A
verts[:, 2:5] = tri.simplices
verts[:, 5:8] = tri.neighbors


time=5000.0           #Gesamtzeit
d_t= .1            #Zeitschritt in sekunden
inter = int(time/d_t)
visu_inter = 10

material = Aluminum


# Gibt die Wearmeleitfähigkeit in die Richtung phi an
def lambda_phi(phi):
    return math.fabs(math.cos(phi)) * material["lambda_x"] + math.fabs(math.sin(phi)) * material["lambda_y"]


# Enthält die Temperatur fuer jede Flaeche
T = np.ones((n_verts))*295.0
T_new = np.zeros((n_verts))

# Wendet die Randbedingung an
def apply_boundary():
    for n in range(n_verts):
        if points[int(verts[n, 2]), 1] == 0 or points[int(verts[n, 3]), 1] == 0 or points[int(verts[n, 4]), 1] == 0 :#or \
            T[n] = 200
        if points[int(verts[n, 2]), 1] >= 4 or points[int(verts[n, 3]), 1] >= 4 or points[int(verts[n, 4]), 1] >= 4:
            T[n] = 1000


# Eine Matrix, die Entfernung, den Winkel, den Waermeleitkoeffizienten und den Koeffizienten fuer die Berechnung fuer jede Flaeche mit jeder anderen Flaeche enthaelt
vert_data = np.zeros((n_verts, n_verts, 4)) # distance, angle, lambda, coefficient


for v1i in range(n_verts):
    p1 = points[int(verts[v1i, 2])]
    p2 = points[int(verts[v1i, 3])]
    p3 = points[int(verts[v1i, 4])]
    
    verts[v1i, 0] = (p1[0]+p2[0]+p3[0])/3
    verts[v1i, 1] = (p1[1]+p2[1]+p3[1])/3
    
    area = p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])
    area = math.fabs(area / 2)
    
    verts[v1i, 8] = area
    for v2i in range(n_verts):
        if v1i == v2i:
            continue
        
        v1 = verts[v1i]
        v2 = verts[v2i]
        
        distance = math.sqrt((v1[0]-v2[0])**2 + (v1[1]-v2[1])**2)
        angle = math.atan2(v1[1]-v2[1], v1[0]-v2[0])
        lambda_nm = lambda_phi(angle)
        coeff = (-lambda_nm * d_t) / (distance * v1[8] * material["dichte"] * material["cp"])
        
        vert_data[v1i, v2i, 0] = distance
        vert_data[v1i, v2i, 1] = angle
        vert_data[v1i, v2i, 2] = lambda_nm
        vert_data[v1i, v2i, 3] = coeff
    
        

# Flaeche (m^2) der Flaeche n
def area(n):
    return verts[n, 8]

# Lambda zwischen n und m
def lambda_nodes(n, m):
    return vert_data[n, m, 2]

# Entfernung zwischen n und m
def distance(n, m):
    return vert_data[n, m, 0]

# Gibt den j-ten Nachbar der Flaeche n zurück (0 <= j < 3)
def neighbor(n, j):
    j = j%3
    return verts[n, 5+j]

# Gibt den Koeffizienten fuer die Berechnung zwischen Flaeche n und m zurueck
def constant(n, m):
    return vert_data[n, m, 3]

# Berechnet den Waermestrom den die Flaeche n erfaehrt
def heat_flux(n):
    flux = 0.0
    
    for j in range(3):
        neigh = int(neighbor(n, j))
        if neigh > -1:
            flux += constant(n, neigh) * (T[n] - T[neigh])
    
    return flux


results = np.zeros((int(inter/visu_inter), n_verts))
print "Begin"
begin = clock()
apply_boundary()
for i in xrange(0,inter):
    # Iteriert ueber alle flaechen
    for n in xrange(n_verts):
        T_new[n] = T[n] + heat_flux(n)
         
    T = T_new
     
    #----Diagramm------------------
    if i % visu_inter == 0 and int(i/visu_inter) < results.shape[0]:
        results[int(i/visu_inter)] = T
     
         
print "Finished"   
print "took " + str(clock() - begin) + " sec"

# Zeigt ergebnisse
visu = GridHistoryVisualization(points, verts, results, tmin=100, tmax=1500)
visu.show()