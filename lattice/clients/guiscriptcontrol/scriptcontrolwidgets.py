from PyQt4 import QtGui
from scriptcontrol import ScriptControl
from twisted.internet.defer import inlineCallbacks

class ScriptControlWidgets():
    def __init__(self, reactor):
        self.makeScriptControl(reactor)
        
        

    @inlineCallbacks
    def makeScriptControl(self, reactor):
        Status = ScriptControl(reactor, self)
        status, params = yield Status.getWidgets()

#    def createExperimentParametersWidget(self, expContext, globalContext):
#        self.experimentParametersWidget = ParametersWidget(self, expContext, globalContext)    
#        return self.sc, self.experimentParametersWidget

        

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    scriptControlWidgets = ScriptControlWidgets(reactor)
    reactor.run()