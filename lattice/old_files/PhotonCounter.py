#!/usr/bin/python

import ok
import gtk, gobject, pango, numarray, math
import threading, socket, time
import pyextfigure

NETPORT = 11115
FREQUENCY = 333   # MHz

#####################################################################
# class gui
#
# The user interface
#####################################################################
class gui:
    #################################################################
    # __init__
    #
    # Create all the labels, menus, boxes etc.
    #################################################################
    def __init__(self):
        self.quitting = False
        self.comm_lock = threading.Lock()
        
        window = gtk.Window()
        window.set_title("PhotonCounter")

        table = gtk.Table(4, 3, True)
        # First, the labels for rows
        table.attach(gtk.Label('Count per sec'),0,1,0,1)
        table.attach(gtk.Label('MMotion Amp/Phase/Bin'),0,1,1,2)
        table.attach(gtk.Label('Integration Time [ms]'),0,1,2,3)
        table.attach(gtk.Label('MMotion Period [bins]'),0,1,3,4)

        # Create a count label
        self.count_label = gtk.Label("-----")
        table.attach(self.count_label, 1, 2, 0, 1)
        # MMotion label
        self.mmotion_label = gtk.Label("-----")
        table.attach(self.mmotion_label, 1, 2, 1, 2)

        # Create a time spinbutton
        self.time_spin = gtk.SpinButton(None, .2, 0)
        self.time_spin.set_range(100, 100000)
        self.time_spin.set_increments(50, 5)
        self.time_spin.set_value(250)
        self.time_spin.connect("value-changed", self.time_changed)
        table.attach(self.time_spin, 1, 2, 2, 3)

        # MMotion Period
        self.period_spin = gtk.SpinButton(None, .2, 0)
        self.period_spin.set_range(2, 64)
        self.period_spin.set_increments(1, 1)
        self.period_spin.set_value(30)
        table.attach(self.period_spin, 1, 2, 3, 4)

	gmeas = gtk.ToggleButton("g2")
        table.attach(gmeas, 2, 3, 0, 1)
	magic = gtk.ToggleButton("Magic")
        table.attach(magic, 2, 3, 1, 2)
        save = gtk.Button(None, gtk.STOCK_SAVE)
        table.attach(save, 2, 3, 2, 3)
        reset = gtk.Button("Reset")
        table.attach(reset, 2, 3, 3, 4)
	
        # create a plot
        self.plot = pyextfigure.Figure()
    
        # put the dactable in the window
        vbox = gtk.VBox()
        vbox.pack_start(table, False, False, 10)
        vbox.pack_start(self.plot, True, True, 0)

        window.add(vbox)

        # connect quit signals 
        window.connect("delete_event", self.on_quit_activate, None)
        window.connect("destroy", self.on_quit_activate, None)
	gmeas.connect("clicked", self.gmeas_clicked, None)
	magic.connect("clicked", self.magic_clicked, None)
	reset.connect("clicked", self.reset_clicked, None)
        save.connect("clicked", self.save_clicked, None)
        # add an idle callback
        gobject.timeout_add(25, self.update_count)
        # Done, show it
        window.show_all()

        self.plot.clear()
        self.plot.set_labels('Time/Frequency', 'Count/s', 'FFT')
        self.plot.set_mode(pyextfigure.DUALTWODPLOT)
       
	self.total_count = 0
	self.mmamp = 0.0
	self.mmphase = 0.0
        self.data = numarray.zeros([64, 2], 'Float32')                    
        # Start network interface
        self.start_network()

        self.time_changed(self.time_spin)

    ################################################################
    # on_quit_activate
    #
    # Run when window is closed
    ################################################################
    def on_quit_activate(self, widget, event, data = None):
        self.quitting = True
        try:
            self.netthread.join()
        except:
            pass
        gtk.main_quit()
        return True
    
    ################################################################
    # reset_clicked
    #
    # Resets the FPGA internals
    ################################################################
    def reset_clicked(self, widget, data = None):
	xem.ActivateTriggerIn(0x40, 0)
	return True
   
    ###############################################################
    # gmeas_clicked
    #
    # Changes whether photons are correlated to RF, or to each other
    ###############################################################
    def gmeas_clicked(self, widget, event, data = None):
        if widget.get_active(): xem.SetWireInValue(0x00, 1)
	else: xem.SetWireInValue(0x00, 0)
        xem.UpdateWireIns()
    	xem.ActivateTriggerIn(0x40, 3)
	return

    ###############################################################
    # magic_clicked
    #
    # Changes whether photons are removed on sync, or keep in queue
    # until they fall out the other end
    ###############################################################
    def magic_clicked(self, widget, event, data = None):
        if widget.get_active(): xem.SetWireInValue(0x00, 0)
	else: xem.SetWireInValue(0x00, 1)
        xem.UpdateWireIns()
    	xem.ActivateTriggerIn(0x40, 2)
	return

    #################################################################################
    # save_clicked
    #
    # Save currently displayed data
    #################################################################################
    def save_clicked(self, widget, data = None):
        filename = 'correlation-' + time.ctime().replace(' ', '-')
        f = file(filename, 'w')
        strdata = ''
	for i in range(64):
	    strdata = strdata + "%i %.4g\n"%(self.data[i,0], self.data[i,1])
        f.write("Bin Count\n")
        f.write(strdata)
        f.close()
        return

    ###############################################################
    # update_count
    #
    # Called every 20ms. Dislpays latest count
    ###############################################################
    def update_count(self):
        time = self.time_spin.get_value()
    	time = int(time*1000.*FREQUENCY/2**17)*(2**17/1000./FREQUENCY)
        # New data?
        if (not self.check_for_data()): return True

        buf = self.fetch_data()
        # normalize wrt time
        data = self.parse_data(buf)*[1, 1000/time, 0]
        fft = self.fft100(data[:,1])
        data[:,2] = fft[:,0]
       
        self.data = data
        total = data[:,1].sum()

	self.total_count = total

        self.count_label.set_markup("<span size='xx-large'>%i</span>"%(total))
        self.plot.new_data(data)
        self.plot.repaint()

        # Figure out the frequency component
        pset = int(self.period_spin.get_value())
        period = fft[:,1].argmax()
        # if (abs( period - pset ) > 10):
        #    period = pset
        self.mmamp = fft[pset,0]
        self.mmphase = fft[pset,1]
        
        self.mmotion_label.set_label("%.4g %.4g %i"%(self.mmamp, self.mmphase,period))

        return True

    def time_changed(self, widget, data = None):
        # Set new integration time
        time = widget.get_value()

        xem.SetWireInValue(0x00, int(time*1000.*FREQUENCY/2**17))
        xem.UpdateWireIns()
        xem.ActivateTriggerIn(0x40, 1)

        return True


    #################################################################################
    # start_network
    #
    # Networked part of the application. Creates a socket, spawns a thread to listen on
    # that socket
    #################################################################################
    def start_network(self):
    	try:
            self.netthread = threading.Thread()
            self.netthread.run = self.listen_to_network
	    hostip = socket.gethostbyname(socket.gethostname())
            self.netsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.netsock.bind((hostip, NETPORT))
            self.netsock.settimeout(.5)
            self.netsock.listen(4)
	    
            self.netthread.start()
	except Exception, e:
	    print "Couldn't start network!", e

    #################################################################################
    # listen_to_network
    #
    # Executed by a separate thread. Listens for connections, if it's a valid
    # command, executes it
    #################################################################################
    def listen_to_network(self):
        while not self.quitting:
            addr = None
            try:
                connsock, addr = self.netsock.accept()
                cmd = connsock.recv(1024)
                if (cmd.rstrip() == "COUNT?"):
                    connsock.sendall("COUNT: %i\n"%(self.total_count))
                elif (cmd.rstrip() == "MMOTION?"):
                    connsock.sendall("MMOTION: %f %f\n"%(self.mmamp, self.mmphase))
		else:
                    connsock.sendall("Bad command #%s#"%(cmd))
		connsock.shutdown(2)
                connsock.close()
            except:
                pass
        self.netsock.close()
        return

    def check_for_data(self):
        buf = '\x00' * 2
        rv = xem.ReadFromPipeOut(0xa0, buf)
        if (buf != '\xED\xFE'):
            return False

        return True

    def fetch_data(self):
        buf = '\x00' * 202
        rv = xem.ReadFromPipeOut(0xa0, buf)
	if (buf[-2:] != '\xED\x0F'):
	    print "Failed with",  map(ord, buf)
	    return None

	buf = buf[0:200]
        return buf

    def parse_data(self, buf):
        data = numarray.zeros([100,3], 'Float32')
        for sample in range(100):
            data[sample][0] = sample;
            data[sample][1] = (255.*ord(buf[2 * sample]) + ord(buf[2 * sample + 1]))
            data[sample][2] = 0

        return data

    def fft100(self, data):
	oversample = 3

        fft = numarray.zeros([100,2], 'Float32')
        for f in range(oversample,100):
            samp = 0.
            camp = 0.
            total = 0.2**
	    samples = int(100 - math.fmod(100,100.*oversample/f))
            for i in range(samples):
                total = total + data[i]
                samp = samp + data[i]*math.sin(2*i*math.pi*f/100./oversample)
                camp = camp + data[i]*math.cos(2*i*math.pi*f/100./oversample)

            if camp == 0: phase = 0
            else: phase = math.atan(samp/camp)
            amp = math.sqrt(samp**2 + camp**2) 

	    if total == 0: fft[f,0] = 0
	    else: fft[f,0] = amp/total
            fft[f,1] = phase

        return fft

xem = ok.FrontPanel()
module_count = xem.GetDeviceCount()

print "Found %d modules"%(module_count)
if (module_count == 0): raise "No XEMs found!"

for i in range(module_count):
    serial = xem.GetDeviceListSerial(i)
    tmp = ok.FrontPanel()
    tmp.OpenBySerial(serial)
    id = tmp.GetDeviceID()
    tmp = None
    if (id == 'Photon Counter'):
        break
if (id  != 'Photon Counter'):
    raise "Didn't find Photon Counter in module list!"

xem.OpenBySerial(serial)
print "Found device called %s"%(xem.GetDeviceID())

print "Loading PLL config"
pll = ok.PLL22150()
xem.GetEepromPLL22150Configuration(pll)
pll.SetVCOParameters(FREQUENCY, 48)
pll.SetDiv1(pll.DivSrc_VCO,4)
pll.SetDiv2(pll.DivSrc_VCO,4)
pll.SetOutputSource(0, pll.ClkSrc_Div1By2)
pll.SetOutputSource(1, pll.ClkSrc_Div1By2)
for i in range(6):
    pll.SetOutputEnable(i, (i == 0))
print "Ref is at %gMHz, PLL is at %gMHz"%(pll.GetReference(), pll.GetVCOFrequency())
for i in range(6):
	if (pll.IsOutputEnabled(i)):
		print "Clock %d at %gMHz"%(i, pll.GetOutputFrequency(i))
		
print "Programming PLL"
#xem.SetEepromPLL22150Configuration(pll)
xem.SetPLL22150Configuration(pll)

print "Programming FPGA"
xem.ConfigureFPGA('/home/labaziew/software/PhotonCounter/PhotonCounter.bit')

# Set font size
gtk.rc_parse_string('style "bigfoot" {font_name = "Sans 15"}')
gtk.rc_parse_string('class "GtkWidget" style "bigfoot"')

app = gui()

# We're threading, init that
gtk.gdk.threads_init()
gtk.gdk.threads_enter()
# Run
try:
    gtk.main()
finally:
    # If we died, let the child thread know
    print "Quitting..."
    app.quitting = True
gtk.gdk.threads_leave()

