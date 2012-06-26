from labrad.server import LabradServer, setting

class MinimalServer(LabradServer):
    """This docstring will appear in the LabRAD helptext."""
    name = "Minimal Server"

    @setting(10, "Echo", data="?", returns="*2v")
    def echo(self, c, data):
        """This docstring will appear in the setting helptext."""
        print type(data)
        return data

if __name__ == "__main__":
    from labrad import util
    util.runServer(MinimalServer())