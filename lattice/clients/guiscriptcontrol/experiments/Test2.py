#import threading
#import time
#import sys


# old Test2
#class Test2():
#    def __init__(self):
#        self.experimentPath = ['Test', 'Exp2']
#        print 'Initializing Test2'
#        self.iterations = 10
#        self.progress = 0.0
#    
#    def pause(self, progress):
#        Continue = self.cxn.semaphore.block_experiment(self.experimentPath, progress)
#        if (Continue == True):
#            self.parameters = self.cxn.semaphore.get_parameter_names(self.experimentPath)
#            return True
#        else:
#            return False     
#        
#    def run(self):
#        import labrad
#        self.cxn = labrad.connect()
#        for i in range(self.iterations):
#            
#            # blocking function goes here
#            self.progress = ((i)/float(self.iterations))*100
#            Continue = self.pause(self.progress)
#            if (Continue == False):
#                self.cxn.semaphore.finish_experiment(self.experimentPath, self.progress)
#                return
#            
#            time.sleep(1)
#            #print 'Test parameters: ', self.parameters
#            print 'goodbye'
#
#        self.progress = 100.0   
#        self.cleanUp()
#        
#    def cleanUp(self):
#        self.cxn.semaphore.finish_experiment(self.experimentPath, self.progress)
#        print 'all cleaned up boss'
#
#if __name__ == '__main__':
#    test2 = Test2()
#    test2.run()

import labrad
import math
import time
from numpy  import *


class Test2():
    def __init__(self):
        self.experimentPath = ['Test', 'Exp2']
        print 'Initializing Test2'
       
    def run(self):
        
        ###### Add Data!!
        
        y1 = [None] * 200
        
        x = arange(24.9, 25.1, .005)
        def generateData():
            for i in range(len(x)):
                p = [.01, 25, .1, 0] #p = [gamma, center, I, offset]
                y1[i] = p[3] + p[2]*(p[0]**2/((x[i] - p[1])**2 + p[0]**2))# Lorentzian
                
        generateData()
        self.cxn = labrad.connect()
        self.cxn.server = self.cxn.data_vault
        self.cxn.data_vault.cd('Sine Curves')
        self.cxn.data_vault.new('Lorentzian', [('x', 'num')], [('y1','Test-Spectrum','num')])
        self.cxn.data_vault.add_parameter('Window', ['Lorentzian'])
        self.cxn.data_vault.add_parameter('plotLive', True)
        for i in range(len(x)):
            self.cxn.data_vault.add([x[i], y1[i]])
            data = [i, y1[i]]
            print data
            time.sleep(.01)
        self.cxn.data_vault.add_parameter('Fit', ['[]', 'Lorentzian', '[0.01, 25.0, 0.10000000000000001, 1.4901161193880158e-08]']) 
        
        ###############################
        
        # now we play the waiting game
        i = 0
        while(i < 200): # timeout
            try:
                Continue = self.cxn.data_vault.get_parameter('Accept-0')
            except:
                Continue = False
            if (Continue == True):
                self.doCalculation()
                break
            else:
                time.sleep(.5)
            i += 1
        self.cleanUp()
        
    def doCalculation(self):
        print 'Accepted!, doing calculation....'
    
    def cleanUp(self):
        print 'why am i not cleaning up?'
        self.cxn.semaphore.finish_experiment(self.experimentPath)
        print 'all cleaned up boss'

if __name__ == '__main__':
    test2 = Test2()
    test2.run()




#cxn.data_vault.add_parameter('Fit', ['[]', 'Line', '[-0.0029498298822661514, 32.067818432564962]'])
#cxn.data_vault.add_parameter('Fit', ['[1, 2]', 'Parabola', '[1, 1, 1]'])
#cxn.data_vault.add_parameter('Garbage', True)
