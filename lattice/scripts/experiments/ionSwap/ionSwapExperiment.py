import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
sys.path.append('/home/lattice/Desktop/LabRAD/lattice/scripts')
sys.path.append('/home/lattice/Desktop/LabRAD/lattice/PulseSequences')
import labrad
import numpy
import time
from scriptLibrary import dvParameters 
from PulseSequences.ionSwap import IonSwapBackground
from crystallizer import Crystallizer
from fly_processing import Binner, Splicer

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    
    def toDict(self):
        return self.__dict__

class IonSwap():
    ''''
    This experiment examines the probability of ions swapping places during heating. 
    After all cooling lights are switched off, the crystal is heated with far blue light for a variable time. Readout is meant to be done with a near resonant light.
    Typically vary:
        axial_heat
        heating delay
    Features:
        729nm used to tag one of the ions to detect position swapping. 854nm used to rebrigthen all the ions.
        866 is switched off together with 397 to prevent cooling when it's not intended
        automatic crystallization routine to reduce necessary time to crystallize the ions
    
    '''
    experimentName = 'IonSwap'
    
    def __init__(self, seqParams, exprtParams):
       #connect and define servers we'll be using
        self.cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = self.cxn.data_vault
        self.rf = self.cxn.trap_drive
        self.pulser = self.cxn.pulser
        self.pmt = self.cxn.normalpmtflow
        self.seqP = Bunch(**seqParams)
        self.expP = Bunch(**exprtParams)
        self.xtal = Crystallizer(self.pulser, self.pmt, self.rf)
        self.Binner = None
        
    def initialize(self):
        #get initialize count for crystallization
        self.xtal.get_initial_rate()
        #directory name and initial variables
        self.dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
        self.topdirectory = time.strftime("%Y%b%d",time.localtime())
        self.setupLogic()
        #get the count rate for the crystal at the same parameters as crystallization
        self.pulser.select_dds_channel('110DP')
        self.pulser.frequency(self.seqP.xtal_freq_397)
        self.pulser.amplitude(self.seqP.xtal_ampl_397)
        self.pulser.select_dds_channel('866DP')
        self.pulser.amplitude(self.seqP.xtal_ampl_866)
        self.programPulser()
        #data processing setup
        self.Binner = Binner(self.seqP.recordTime, self.expP.binTime)
        self.Splicer = Splicer(self.seqP.startReadout, self.seqP.endReadout)
        
    def setupCamera(self):
        # tell the camera to start waiting for data
        
        # height, width, iterations, numAnalyzedImages
        self.cxn.andor_ion_count.collect_data((self.expP.vend - self.expP.vstart + 1), (self.expP.hend - self.expP.hstart + 1), self.expP.iterations, self.expP.numAnalyzedImages)

    
    def setupLogic(self):
        self.pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False)
    
    def programPulser(self):
        seq = IonSwapBackground(self.pulser)
        self.pulser.new_sequence()
        seq.setVariables(**self.seqP.toDict())
        seq.defineSequence()
        self.pulser.program_sequence()
        self.seqP['recordTime'] = seq.parameters.recordTime
        self.seqP['startReadout'] = seq.parameters.startReadout
        self.seqP['endReadout'] = seq.parameters.endReadout
    
    def run(self):
        sP = self.seqP
        xP = self.expP
        initpower = self.rf.amplitude()
        self.rf.amplitude(xP.rf_power)
        time.sleep(xP.rf_settling_time)
        self.setupCamera()
        self.initialize()
        self.sequence()
        self.finalize()
        self.rf.amplitude(initpower)
        print 'DONE {}'.format(self.dirappend)

    def sequence(self):
        sP = self.seqP
        xP = self.expP
        #saving timetags
        self.dv.cd(['','Experiments', self.experimentName, self.topdirectory, self.dirappend], True)
        self.dv.new('timetags',[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
        #do iterations
        for iteration in range(xP.iterations):
            print 'recording trace {0} out of {1}'.format(iteration+1, xP.iterations)
            self.pulser.reset_timetags()
            self.pulser.start_single()
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            timetags = self.pulser.get_timetags().asarray
            iters = iteration * numpy.ones_like(timetags) 
            self.dv.add(numpy.vstack((iters,timetags)).transpose())
            #add to binning of the entire sequence
            self.Binner.add(timetags)
            self.Splicer.add(timetags)
            #auto crystallization
            if xP.auto_crystal:
                success = self.xtal.auto_crystallize()
                if not success: break
        #adding readout counts to data vault:
        readout = self.Splicer.getList()
        self.dv.cd(['','Experiments', self.experimentName, self.topdirectory, self.dirappend])
        self.dv.new('readout',[('Iter', 'Number')], [('PMT counts','Counts/Sec','Counts/Sec')] )
        self.dv.add(readout)
        #adding binned fluorescence to data vault:
        binX, binY = self.Binner.getBinned()
        self.dv.cd(['','Experiments', self.experimentName, self.topdirectory, self.dirappend])
        self.dv.new('binned',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
        data = numpy.vstack((binX, binY)).transpose()
        self.dv.add(data)
        self.dv.add_parameter('Window',['Binned Fluorescence'])
        self.dv.add_parameter('plotLive',True)
        #adding histogram of counts to data vault
        binX, binY = self.Splicer.getHistogram()
        self.dv.cd(['','Experiments', self.experimentName, self.topdirectory, self.dirappend])
        self.dv.new('histogram',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
        data = numpy.vstack((binX, binY)).transpose()
        self.dv.add(data)
        self.dv.add_parameter('Window',['Histogram'])
#        self.dv.add_parameter('plotLive',True)
        # gathering parameters and adding them to data vault
        measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP', 'pulser']
        measuredDict = dvParameters.measureParameters(self.cxn, self.cxnlab, measureList)
        dvParameters.saveParameters(self.dv, measuredDict)
        dvParameters.saveParameters(self.dv, sP.toDict())
        dvParameters.saveParameters(self.dv, xP.toDict())
    
    def finalize(self):
        for name in ['axial', '110DP']:
            self.pulser.switch_manual(name)
        below, above = self.Splicer.getPercentage(self.expP.threshold)
        print '{0:.1f}% of samples are Melted, below threshold of {1} '.format(100 * below, self.expP.threshold)
        print '{0:.1f}% of samples are Crystallized, above threshold of {1} '.format(100 * above, self.expP.threshold)
    
    def __del__(self):
        self.cxn.disconnect()
       
if __name__ == '__main__':
    #experiment parameters
    exposure = 100*10**-3
    hstart   = 455
    hend     = 530
    vstart   = 217
    vend     = 242    


    cxn = labrad.connect()
    cameraServer = cxn.andor_ion_count
    temp = cameraServer.get_current_temperature()
    print temp
    
    # set up camera
    try:
        cameraServer.set_trigger_mode(1)
    except:
        print 'still acquiring, aborting..'
        cameraServer.abort_acquisition()
        cameraServer.set_trigger_mode(1)
    cameraServer.set_read_mode(4)
    cameraServer.set_emccd_gain(255)
    cameraServer.set_exposure_time(exposure)   
    cameraServer.cooler_on()
    cameraServer.set_image_region(1, 1, hstart, hend, vstart, vend)
    
    cameraServer.clear_image_array()
    
    numberKineticSets = 2
    for kinSet in range(numberKineticSets):
        params = {
              'exposure': exposure,                 
              'initial_cooling': 25e-3,
              'camera_delay': 20*10**-3,
              'darkening': 10*10**-3,
              'heat_delay':10e-3,
              'axial_heat':12*10**-3,
              'readout_delay':100.0*10**-9,
              'readout_time':10.0*10**-3,
              'rextal_time': 25*10**-3,
              'cooling_ampl_866':-11.0,
              'heating_ampl_866':-11.0,
              'readout_ampl_866':-11.0,
              'xtal_ampl_866':-11.0,
              'cooling_freq_397':103.0,
              'cooling_ampl_397':-13.5,
              'readout_freq_397':115.0,
              'readout_ampl_397':-13.5,
              'xtal_freq_397':103.0,
              'xtal_ampl_397':-11.0,
              'brightening': 5*10**-3,
              'repumpPower':-3.0 
              }
        
        exprtParams = {
                       'iterations':2,
                       'rf_power':-3.5, #### make optional
                       'rf_settling_time':0.3,
                       'auto_crystal':True,
                       'pmtresolution':0.075,
                       'detect_time':0.225,
                       'binTime':250.0*10**-6,
                       'hstart': hstart,
                       'hend': hend,
                       'vstart': vstart,
                       'vend': vend,
                       'numAnalyzedImages': 2, # immediately before and after axial heating
                       'typicalIonDiameter': 5,
                       'threshold': 35000
                       }

                
        exprt = IonSwap(params,exprtParams)
        exprt.run()
        numKin = ((exprtParams['numAnalyzedImages'] + 1)*exprtParams['iterations'])
        cameraServer.get_acquired_data_kinetic(numKin)
        cameraServer.save_to_data_vault_kinetic(str(['','Experiments', exprt.experimentName, exprt.topdirectory, exprt.dirappend, 'Scans']), ('Kinetic Set - ' + str(kinSet)), (exprtParams['numAnalyzedImages'] + 1)*exprtParams['iterations'])