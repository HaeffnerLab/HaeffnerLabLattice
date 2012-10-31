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