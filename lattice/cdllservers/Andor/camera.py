from andor import *
import time
import sys
import signal
from optparse import OptionParser
import menusystem
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from pylab import *
import matplotlib.pyplot as plt 
import matplotlib.animation as animation

#############################
#    parsing the options    #
#############################

parser = OptionParser()
parser.add_option("-T", "--temperature", dest="Tset", help="setpoint temperature in C [-95 to +25]", default=-20, type="int")
parser.add_option("-G", "--gain", dest="EMCCDGain", help="EMCCD gain [2 to 300]", default=255, type="int")
parser.add_option("-p", "--preamp-gain", dest="PreAmpGain", help="preamp gain [0 to 2]", default=0, type="int")
parser.add_option("-t", "--exposure-time", dest="ExposureTime", help="exposure time in seconds", default=0.1, type="float")
parser.add_option("--trigger-mode", dest="TriggerMode", help="trigger mode (0: int, 1: ext, 7: bulb, 10: soft)", default=7, type="int")
parser.add_option("--cooler-on",action="store_true", dest="CoolerOn", help="turn on the cooler", default=False)
parser.add_option("--cooler-mode",action="store_true", dest="CoolerMode", help="Leave the cooler on after shutdown", default=False)
parser.add_option("--stabilise",action="store_true", dest="stabilise", help="stabilise the temperature before acquisition", default=False)
parser.add_option("--rotate", dest="rotate", help="rotate the image (0: no rotation, 1: 90deg clockwise, 2: 90deg anti clockwise", type=int, default=0)
parser.add_option("--start-acquisition",action="store_true", dest="acquisition", help="start acquisition right away", default=False)
parser.add_option("-v", "--verbose",action="store_true", dest="verbosity", default=False, help="causes the script to verbose")

(options, args) = parser.parse_args()

Tset = options.Tset
EMCCDGain = options.EMCCDGain
PreAmpGain = options.PreAmpGain
ExposureTime = options.ExposureTime
TriggerMode = options.TriggerMode
CoolerMode = options.CoolerMode
CoolerOn = options.CoolerOn
stabilise = options.stabilise
acquisition = options.acquisition
rotate = options.rotate
verbosity = options.verbosity

if len(args) > 0:
    filename = args[0]
else:
    filename = 'image'

#############################
#       menu functions      #
#############################

def signal_handler(signal, frame):
    global menu
    try:
            menu
    except NameError:
            menu = None

    if menu is None:
        print "shutting down the camera ..."
        cam.ShutDown()
        sys.exit()
    else:
        menu.run()

signal.signal(signal.SIGINT, signal_handler)

def snap(name, iterator):
    global cam
    print "Ready for Acquisition..."
    cam.StartAcquisition()
    data = []
    cam.GetAcquiredData(data)    
    #cam.SaveAsBmpNormalised("%s%03g.bmp" %(name, iterator))
    #cam.SaveAsBmp("test.bmp")
    print "captured %s%03g" %(name, iterator)
#    newdata = np.array(cam.imageArray)
#    newdata = np.reshape(newdata, (cam.width, -1))
#    matshow(newdata)
#    show()
    cam.SaveAsTxt("%s%03g.txt" %(name, iterator))   

def snap_continuous():
    global cam
    
    width = cam.width
    height = cam.height
    
    print "Ready for Acquisition..."
    cam.StartAcquisition()
    
    #cam.dll.WaitForAcquisition()
    data = []
    cam.GetMostRecentImage(data)
    #newdata = np.array(cam.imageArray[0:3000])
    #print newdata.shape
    #newdata = np.reshape(newdata, (height, width))
    newdata = np.reshape(cam.imageArray, (height, width))
 
  
    fig = plt.figure()
        
    im = plt.matshow(newdata)#, cmap=plt.get_cmap('jet'))
    def updatefig(*args):
        cam.dll.WaitForAcquisition()
        data = []
        cam.GetMostRecentImage(data)
        #newdata = np.array(cam.imageArray[0:3000])
        #print newdata.shape
        #newdata = np.reshape(newdata, (height, width))
        newdata = np.reshape(cam.imageArray, (height, width))
        im.set_array(newdata)
        return im,

    ani = animation.FuncAnimation(fig, updatefig, blit=True)
    plt.show()    
    
    cam.AbortAcquisition()

def snap_kinetic_internal(name, iterator):
    global cam
    
    numKin = int(raw_input('Enter number of snapshots: '))    
    cam.SetNumberKinetics(numKin)
    
    kinCycleTime = float(raw_input('Enter kinetic cycle time: '))
    cam.SetKineticCycleTime(kinCycleTime)    
    
    cam.StartAcquisition()
    cam.dll.WaitForAcquisition()
    
    data = []
    cam.GetAcquiredData(data, numKin)    

    print "captured %s%03g" %(name, iterator)
    cam.SaveAsTxt("%s%03g.txt" %(name, iterator))
        
def menu_status():
    global menu
    global cam

    print menu.seperator + menu.nl
    Tstatus = cam.GetTemperature()
    cam.GetEMCCDGain()
    Tset = cam.set_T

    print menu.prefix + "Temperature is %g [Set T: %i, %s]" %(cam.temperature, Tset, Tstatus)
    print menu.prefix + "Gain is %i, preAmp gain is %i" % (cam.gain, cam.preampgain)
    return False

def menu_set_temperature():
    global menu
    global cam

    print menu.seperator + menu.nl
    Tset = raw_input(menu.prefix + "Enter the set temperature [-95 .. +20]: ")
    cam.SetTemperature(Tset)
    return False

def menu_set_exposure():
    global menu
    global cam

    print menu.seperator + menu.nl
    set_t = float(raw_input(menu.prefix + "Enter the exposure time is seconds: "))
    cam.SetExposureTime(set_t)
    return False

def menu_turn_on_cooler():
    global cam
    cam.CoolerON()
    return False

def menu_turn_off_cooler():
    global cam
    cam.CoolerOFF()
    return False

def menu_start_acquisition():
    global filename
    global iteration
    global TriggerMode

    cam.SetTriggerMode(TriggerMode)

    while True:
            iteration += 1
            snap(filename, iteration)

    return False

def menu_capture_snapshot():
    global filename
    global iteration
    global cam

    cam.SetTriggerMode(0)

    snap(filename, iteration)
    iteration += 1

    return False

def menu_capture_video():
    global cam
    
    cam.SetTriggerMode(0)
    cam.SetAcquisitionMode(5) 
    
    snap_continuous()
    
    return False

def menu_start_kinetic_internal():
    global cam
    global filename
    global iteration
        
    cam.SetTriggerMode(0)
    cam.SetAcquisitionMode(3)
    
    snap_kinetic_internal(filename, iteration)
    
    return False

def menu_quit():
    print "Shutting down the camera..."
    cam.ShutDown()
    sys.exit()

#############################
#   Initialise the camera   #
#############################

cam = Andor()

if verbosity:
    cam.verbosity = True

cam.SetSingleScan()
cam.SetTriggerMode(TriggerMode)
cam.SetShutter(1,1,0,0)
cam.SetPreAmpGain(PreAmpGain)
cam.SetEMCCDGain(EMCCDGain)
cam.SetExposureTime(ExposureTime)
cam.SetImageRotate(rotate)

if CoolerMode is True:
    cam.SetCoolerMode(1)

cam.SetTemperature(Tset)

if CoolerOn is True:
    cam.CoolerON()

if stabilise is True:
    print "Stabilising the temperature..."
    if not cam.IsCoolerOn():
        cam.CoolerON()
    while cam.GetTemperature() is not 'DRV_TEMP_STABILIZED':
        print "Temperature is: %g [Set T: %g, %s]" % (cam.temperature, Tset, cam.GetTemperature())
        time.sleep(10)

#############################
#         Main menu         #
#############################

menu = menusystem.menu_system('\nmain menu\n---------\n', '\n$ ')
menu.nl = '\n'
menu.prefix='   '
menu.seperator = ''
menu.add_entry('1', 'view the current status', menu_status)
menu.add_seperator()
menu.add_entry('2', 'set the temperature', menu_set_temperature)
menu.add_entry('3', 'turn on the cooler', menu_turn_on_cooler)
menu.add_entry('4', 'start acquisition [EXT Trig]', menu_start_acquisition)
menu.add_entry('5', 'set the exposure time', menu_set_exposure)
menu.add_entry('6', 'capture a single snapshot [Soft Trig]', menu_capture_snapshot)
menu.add_entry('7', 'turn off the cooler', menu_turn_off_cooler)
menu.add_entry('8', 'capture in video mode', menu_capture_video)
menu.add_entry('9', 'start a kinetic series [Soft Trig]', menu_start_kinetic_internal)
menu.add_seperator()
menu.add_entry('q', 'quit', menu_quit)

iteration = 0

if acquisition is True:
    menu_start_acquisition()
else:
    menu.run('1')
