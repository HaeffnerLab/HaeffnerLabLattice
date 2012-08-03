from labrad.server import LabradServer, setting
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

class Semaphore(LabradServer):
    """Houses the Blocking Function"""
    name = "Semaphore"
    
    blockFlag = False
    value = 0

    @inlineCallbacks            
    def _block(self):
        i = 0
        while(1):
            i += 1
            yield deferToThread(time.sleep, .5)
            print 'blocking!', i
            print self.blockFlag
            if (self.blockFlag == False):
                returnValue(True)

    @setting(10, "Block", returns="b")
    def block(self, c):
        """Update and get the number."""
        result = self._block()
        return result
    
    @setting(11, "Set Flag", flag = "b", returns="")
    def setFlag(self, c, flag):
        """Set blocking flag"""
        self.blockFlag = flag
        print self.blockFlag

    @setting(12, "Set Value", returns="")
    def setValue(self, c):
        """Set Value"""
        self.value += 5
        print self.value        

    @setting(13, "Get Value", returns="i")
    def getValue(self, c):
        """Get Value"""
        return self.value        


if __name__ == "__main__":
    from labrad import util
    util.runServer(Semaphore())