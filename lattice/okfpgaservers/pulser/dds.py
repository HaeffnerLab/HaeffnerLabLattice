from labrad.server import LabradServer, setting, Signal

class DDS(LabradServer):
    """Contains the DDS functionality for the pulser server"""
    
    @setting(40, 'Add DDS Pulses', channel = 's', values = '*(vv)')
    def addDDSPulse(self, c, channel, values):
        """Takes the name of the DDS channel, and the list of values in the form [(start, frequency, amplitude)]
        where frequency is in MHz, and amplitude is in dBm
        """
        hardwareAddr = self.ddsDict.get(channel).channelnumber
        sequence = c.get('sequence')
        #simple error checking
        if hardwareAddr is None: raise Exception("Unknown DDS channel {}".format(channel))
        if not sequence: raise Exception ("Please create new sequence first")
        
        