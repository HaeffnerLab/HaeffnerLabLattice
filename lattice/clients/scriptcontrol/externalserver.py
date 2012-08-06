from labrad.server import LabradServer, setting

class ExternalServer(LabradServer):
    """External Server to test the blocking funtion."""
    name = "External Server"

    currentNumber = 0

    def updateNumber(self):
        self.currentNumber += 1

    @setting(10, "Get Number", returns="i")
    def getNumber(self, c, data):
        """Update and get the number."""
        self.updateNumber()
        return self.currentNumber

if __name__ == "__main__":
    from labrad import util
    util.runServer(ExternalServer())