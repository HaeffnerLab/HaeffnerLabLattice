from labrad.server import LabradServer, Signal

class Signals(LabradServer):
    
    on_new_status = Signal(200000 , "on new script status", 'wsv')