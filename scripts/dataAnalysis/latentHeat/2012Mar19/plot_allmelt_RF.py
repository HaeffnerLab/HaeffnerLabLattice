# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 17:18:54 2012
"""
import matplotlib

from matplotlib import pyplot 

t1 = [50, 60, 70, 80, 90, 100, 110, 120]
t2 = [60, 70, 80, 90, 100, 110, 120, 130]
t3 = [70,80,90,100,110,110,120]
t4=[70,80,90,100,110]
p1=[0.0, 0.01, 0.0, 0.05, 0.07, 0.29, 0.36, 0.64]
p2 = [.03, 0.11, 0.18, 0.37, 0.72, 0.7, 0.88, 0.94]
p3 = [.01, 0.17, 0.44, 0.93, 0.93, 0.98, 1.0]
p4=[.01, 0.08, 0.12, 0.49, 0.87]

figure = pyplot.figure()
l1 = pyplot.plot(t1, p1, '-og',label='-3.5 dBm')
pyplot.hold(True)
l2 = pyplot.plot(t2, p2, '-ob',label='-2.0 dBm')
l3 = pyplot.plot(t3, p3, '-ok',label='0.0 dBm')
l4 = pyplot.plot(t4, p4, '-or',label='2.0 dBm')
pyplot.ylim([0,1])
pyplot.xlim([50,130])
pyplot.xlabel('Heating time (ms)')
pyplot.ylabel('Melted fraction')
figure.legend((l1,l2,l3,l4), ('-3.5 dBm', '-2.0 dBm', '0.0 dBm', '2.0 dBm'))