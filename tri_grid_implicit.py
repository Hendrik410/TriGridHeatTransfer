'''
Created on 02.08.2017

@author: muel_hd
'''

import math
from time import clock
import numpy as np
import numpy.linalg as la
import scipy.spatial as sp

from materials import SiC, Aluminum
from visualization import GridHistoryVisualization

points = np.zeros((400, 2)) # x, y

for x in range(20):
    for y in range(20):
        points[x * 20 + y] = [x/2.0, y/2.0]


# generate points somehow

tri = sp.Delaunay(points)
n_verts = tri.simplices.shape[0]

verts = np.zeros((n_verts, 9)) # x, y, p1, p2, p3, n1, n2, n3, A
verts[:, 2:5] = tri.simplices
verts[:, 5:8] = tri.neighbors


time=500.0           #Gesamtzeit
d_t= .1              #Zeitschritt in sekunden
inter = int(time/d_t)
visu_inter = 10

material = Aluminum



def lambda_phi(phi):
    return math.fabs(math.cos(phi)) * material["lambda_x"] + math.fabs(math.sin(phi)) * material["lambda_y"]



T = np.ones((n_verts))*295.0
T_new = np.zeros((n_verts))

def apply_boundary():
    for n in range(n_verts):
        if points[int(verts[n, 2]), 1] == 0 or points[int(verts[n, 3]), 1] == 0 or points[int(verts[n, 4]), 1] == 0 :#or \
        #points[int(verts[n, 2]), 0] == 9 or points[int(verts[n, 3]), 0] == 9 or points[int(verts[n, 4]), 0] == 9:
            T[n] = 1000
        #if points[int(verts[n, 2]), 0] == 0 or points[int(verts[n, 3]), 0] == 0 or points[int(verts[n, 4]), 0] == 0 or \
        if points[int(verts[n, 2]), 1] == 9 or points[int(verts[n, 3]), 1] == 9 or points[int(verts[n, 4]), 1] == 9:
            T[n] = 100

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
    
        

def area(n):
    return verts[n, 8]

def lambda_nodes(n, m):
    return vert_data[n, m, 2]

def distance(n, m):
    return vert_data[n, m, 0]

def neighbor(n, j):
    j = j%3
    return verts[n, 5+j]

def constant(n, m):
    return vert_data[n, m, 3]


coeff = np.zeros((n_verts, n_verts))

for n in xrange(n_verts):
    c = 1.0
    
    for j in range(3):
        neigh = int(neighbor(n, j))
        if neigh > -1:
            c = c + constant(n, neigh)
            
            coeff[n, neigh] = constant(neigh, n)
        
    coeff[n, n] = -c


apply_boundary()
results = np.zeros((int(inter/visu_inter) + 1, n_verts))
results[0] = T

print "Begin"
begin = clock()
for i in xrange(0,inter):
    
    T_new = la.solve(coeff, T)
    
    T = T_new
    
    #----Diagramm------------------
    if i % visu_inter == 0 and int(i/visu_inter) < results.shape[0]:
        results[int(i/visu_inter) + 1] = T
    
    apply_boundary()
         
print "Finished"   
print "took " + str(clock() - begin) + " sec"

visu = GridHistoryVisualization(points, verts, results, tmin=0, tmax=2000)
visu.show()