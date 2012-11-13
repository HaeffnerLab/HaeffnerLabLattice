# THIS SERVER DOESN'T USE OTHER LABRAD MODULES
# BUT RATHER USES THE PYTHON SERIAL LIBRARY
# TO COMMUNICATE WITH SERIAL DEVICES.

from labrad.server import LabradServer, setting
from labrad.types import Error
from serial import Serial, SerialException

NAME = 'Serial Device ver 0'

class SerialDeviceError( Exception ):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SerialDeviceServer( LabradServer ):
    """Base class for serial device servers."""
    name = "%LABRADNODE%" + " " + NAME
    ser = None

    class SerialConnection():
        def __init__(self, ser=None):
            self.write = lambda x: ser.write(x)
            self.read = lambda: ser.read_line()
            self.close = lambda: ser.close()

    def initSerial(self, port=None):
        try:
            while not port:
                print 'Enter serial port (must enter something):'
                port = raw_input()
            return self.SerialConnection( ser = Serial(port) )
        #make this more specific
        except SerialException:
            raise SerialDeviceError( 'could not connect to serial server' )
    
        
    # Server startup and shutdown
    def initServer(self):
        """
        Establish serial connection.
        """
        self.ser = self.initSerial()
    
    def stopServer(self):
        """Stop the server.

        Called when the server is shutting down, but before we have
        closed any client connections.  Perform any cleanup operations here.
        """
        if self.ser:
            self.ser.close()


if __name__ == "__main__":
    from labrad import util
    util.runServer(SerialDeviceServer())
