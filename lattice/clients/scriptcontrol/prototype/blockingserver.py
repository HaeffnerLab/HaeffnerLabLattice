from labrad.server import LabradServer, setting
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

class Semaphore(LabradServer):
    """Houses the Blocking Function"""
    name = "Semaphore"
    
    blockFlag = False
    value = 0
    killSwitch = False
    
    blockFlag2 = False
    value2 = 0
    killSwitch2 = False    

    @inlineCallbacks            
    def _block(self):
        i = 0
        while(1):
            i += 1
            yield deferToThread(time.sleep, .5)
            print 'blocking!', i
            print self.blockFlag
            if (self.blockFlag == False):
                returnValue(self.killSwitch)

    @inlineCallbacks            
    def _block2(self):
        i = 0
        while(1):
            i += 1
            yield deferToThread(time.sleep, .5)
            print 'blocking!', i
            print self.blockFlag2
            if (self.blockFlag2 == False):
                returnValue(self.killSwitch2)



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
    
    @setting(14, "Set Kill Switch", switch = 'b', returns="")
    def setKillSwitch(self, c, switch):
        """Set Kill Switch"""
        self.killSwitch = switch
  
    @setting(15, "Block2", returns="b")
    def block2(self, c):
        """Update and get the number."""
        result = self._block2()
        return result
    
    @setting(16, "Set Flag2", flag = "b", returns="")
    def setFlag2(self, c, flag):
        """Set blocking flag2"""
        self.blockFlag2 = flag
        print self.blockFlag2

    @setting(17, "Set Value2", returns="")
    def setValue2(self, c):
        """Set Value2"""
        self.value2 += 5
        print self.value2        

    @setting(18, "Get Value2", returns="i")
    def getValue2(self, c):
        """Get Value2"""
        return self.value2   
    
    @setting(19, "Set Kill Switch2", switch = 'b', returns="")
    def setKillSwitch2(self, c, switch):
        """Set Kill Switch"""
        self.killSwitch2 = switch



if __name__ == "__main__":
    from labrad import util
    util.runServer(Semaphore())