'''
Created on 25.07.2017

@author: muel_hd
'''

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider



class GridHistoryVisualization:
    
    def __init__(self, points, vertices, temperatures, tmin=None, tmax=None):
        self.points = points
        self.vertices = vertices
        self.temperatures = temperatures
        self.point_in_time = -1
        
        if tmin is None:
            tmin = temperatures.min()
        
        if tmax is None:
            tmax = temperatures.max()
        
        self.tmin = tmin
        self.tmax = tmax
        
        self.slider_ax = None
        self.grid_ax = None
        self.slider = None
        
        
        
    def show(self):
        fig = plt.figure()
    
        self.grid_ax = fig.add_axes([0.1, 0.2, 0.8, 0.7])
        self.slider_ax = fig.add_axes([0.1, 0.1, 0.8, 0.03])
        self.slider = Slider(self.slider_ax, "Time", 0, self.temperatures.shape[0] - 1)
        self.slider.on_changed(self.slider_changed)
        
        self.show_frame(0)
        
        plt.show(block=True)
        
    def show_frame(self, time):
        if self.point_in_time == time:
            return
        
        self.grid_ax.tripcolor(self.points[:,0], 
                               self.points[:,1], 
                               self.vertices, 
                               facecolors=self.temperatures[time, :], 
                               cmap="plasma",
                               vmin=self.tmin,
                               vmax=self.tmax)
        
        self.point_in_time = time
        
    def slider_changed(self, val):
        self.show_frame(int(val))


