# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 17:18:54 2012

@author: italk
"""
import matplotlib
import numpy as np
matplotlib.use('Qt4Agg')
from matplotlib import pyplot 

t1 = np.arange(45,86,10) #30
t2 = np.arange(45,86,10) #15
t3 = np.arange(35,76,10) # 0
t4 = np.arange(25,66,10) # -15
t5 = np.arange(25,66,10) # -30

p1 = [0.0, 0.06, 0.47, 0.99, 1.0]
p2 = [.02, 0.02, 0.37, 0.82, 1.0]
p3 = [.02, 0.18, 0.42, 0.88, 0.99]
p4 = [.0, 0.02, 0.31, 0.73, 0.89]
p5 = [.01, 0.14, 0.6, 0.92, 0.98]

figure = pyplot.figure()
l1 = pyplot.plot(t1, p1, '-og')#,label='30 V')
pyplot.hold(True)
l2 = pyplot.plot(t2, p2, '-oc')#,label='15 V')
l3 = pyplot.plot(t3, p3, '-ok')#,label='0 V')
l4 = pyplot.plot(t4, p4, '-or')#,label='-15 V')
l5 = pyplot.plot(t5, p5, '-ob')#,label='-30 V')
pyplot.ylim([0,1])
pyplot.xlim([20,90])
pyplot.xlabel('Heating time (ms)')
pyplot.ylabel('Melted fraction')
figure.legend((l1,l2,l3,l4,l5), ('30 V','15 V','0 V','-15 V','-30 V'))