# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 12:39:01 2017

@author: eli
"""

''' Present an interactive function explorer with slider widgets.
Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve sliders.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/MS_gate_bokeh
in your browser.
'''
import numpy as np
import csv
import math
from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure


def getP2(alpha, gama, nbar):
    P2 = 1.0 / 8.0 * (3.0 + math.e ** ((-16 * (abs(alpha) ** 2) * (nbar + 0.5))) + 4 * math.cos(4 * gama) * math.e ** ((
    -4 * (abs(alpha) ** 2) * (nbar + 0.5))))
    return P2

def getP1(alpha, gama, nbar):
    P1 = 1.0/ 4.0 * (1 - math.e ** (((-16 * (abs(alpha) ** 2)*(nbar+0.5)))))
    return P1

def getP0(alpha, gama , nbar):
    P0 = 1.0 / 8.0 * (3.0 + math.e ** ((-16 * (abs(alpha) ** 2) * (nbar + 0.5))) - 4 * math.cos(4 * gama) * math.e ** ((
    -4 * (abs(alpha) ** 2) * (nbar + 0.5))))
    return P0


# Set up plot
# Set up data
t = np.linspace(0, 0.00030, 10)*1000000.0
plot = figure(plot_height=600, plot_width=600, title="MS gate",
              tools="crosshair,pan,reset,save,wheel_zoom",  
              x_range=[min(t), max(t)], y_range=[0, 1.05]
              ,x_axis_label= 'time [us]', y_axis_label='probability')

P0_source = ColumnDataSource(data=dict(x=t, y=0*t ))
P1_source = ColumnDataSource(data=dict(x=t, y=0*t ))
P2_source = ColumnDataSource(data=dict(x=t, y=0*t ))
P0_experiment_source = ColumnDataSource(data=dict(x=t, y=0*t ))
P1_experiment_source = ColumnDataSource(data=dict(x=t, y=0*t ))
P2_experiment_source = ColumnDataSource(data=dict(x=t, y=0*t ))

#plot.multi_line('x', 'y', source=source, line_width=3, line_alpha=0.6)
plot.line('x', 'y', source=P0_source, line_width=3, line_alpha=0.6,color='red')
plot.line('x', 'y', source=P1_source, line_width=3, line_alpha=0.6,color='green')
plot.line('x', 'y', source=P2_source, line_width=3, line_alpha=0.6,color='blue')
plot.circle( 'x', 'y', source=P0_experiment_source,color='red', size=6 , legend='SS'  ) #,'green','blue'] 
plot.circle( 'x', 'y', source=P1_experiment_source,color='green', size=6, legend='SD+DS'   ) #,'green','blue'] 
plot.circle( 'x', 'y', source=P2_experiment_source,color='blue', size=6, legend='DD   '   ) #,'green','blue']     


# Set up widgets
path = TextInput(title="file path", value='my sine wave')
file_name = TextInput(title="file name", value='1203_24')
etta = Slider(title="etta", value=0.08637, start=0.0, end=0.15, step=0.01)
#delta = Slider(title="delta [KHz]", value=0.08637, start=0.0, end=0.15, step=0.01)
Pi_time = Slider(title="pi_time [us]", value=9.6, start=5, end=15, step=0.05)
n_bar = Slider(title="n_bar", value=0.0, start=0.0, end=10, step=0.1)
chi = TextInput(title="chi", value='7.0')



# Set up callbacks
def update_exp_data(attrname, old, new):
    # set up the data
    try:

        #csv_reader = csv.reader(open('00001 - MS Gate 2017Sep13_1203_24.csv'))
        print file_name.value
        csv_reader = csv.reader(open('00001 - MS Gate 2017Sep13_'+ file_name.value+'.csv'))
        global t
    
        t=[]
        P0_experiment = []
        P1_experiment = []
        P2_experiment = []

        for j in csv_reader:
            t.append(float(j[0]))
            P0_experiment.append(float(j[1]))
            P1_experiment.append(float(j[2]))
            P2_experiment.append(float(j[3]))

      
        P0_experiment_source.data = dict(x=t, y=P0_experiment)
        P1_experiment_source.data = dict(x=t, y=P1_experiment)
        P2_experiment_source.data = dict(x=t, y=P2_experiment)
    
    except:
        print "could not open file, doesnt exist"

    
    



file_name.on_change('value', update_exp_data)
path.on_change('value', update_exp_data)

def update_data(attrname, old, new):
    global t 

    delta = 2 * math.pi * 17.5 * 10 ** 3

    # Get the current slider values
    eta = etta.value
    pi_time = Pi_time.value
    nbar = n_bar.value
    
    omega = math.pi / (pi_time * 10 ** (-6))
    lamda = 1.0*(eta*omega)**2/delta
    kai = 1.0*(eta*omega/delta)**2
    
    

    

    P0_theory = []
    P1_theory = []
    P2_theory = []
    time = []

    for ts in t:
        ts=ts/1000000.0
        gama = 1.0*lamda*ts-kai*math.sin(delta*ts)
        alpha = 1.0*(eta * omega / delta) * (math.e ** (1j * delta * ts) - 1)
        a0 = getP0(alpha, gama, nbar)
        a1 = getP1(alpha, gama, nbar)
        a2 = getP2(alpha, gama, nbar)

        P0_theory.append(a0)
        P1_theory.append(a1)
        P2_theory.append(a2)
        time.append(ts*1000000.0)

    #print P0_theory+P1_theory+P2_theory
    P0_source.data = dict(x=time, y=P0_theory)
    P1_source.data = dict(x=time, y=P1_theory)
    P2_source.data = dict(x=time, y=P2_theory)
    chi.value='hi'
    

for w in [etta, Pi_time, n_bar]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = widgetbox(path, file_name, etta, Pi_time, n_bar,chi)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Sliders"