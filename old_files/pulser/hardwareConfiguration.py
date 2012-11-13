class channelConfiguration():
    """
    Stores complete configuration for each of the channels
    """
    def __init__(self, channelNumber, ismanual, manualstate,  manualinversion, autoinversion):
        self.channelnumber = channelNumber
        self.ismanual = ismanual
        self.manualstate = manualstate
        self.manualinv = manualinversion
        self.autoinv = autoinversion

class hardwareConfiguration():
    isProgrammed = False
    sequenceType = None #none for not programmed, can be 'one' or 'infinite'
    collectionMode = 'Normal' #default PMT mode
    collectionTime = {'Normal':0.100,'Differential':0.100} #default counting rates
    channelDict = {
                   '866DP':channelConfiguration(0, False, True, True, False),
                   'crystallization':channelConfiguration(1, True, False, False, False),
                   'bluePI':channelConfiguration(2, True, False, True, False),
                   '110DP':channelConfiguration(3, False, True, True, False),
                   'axial':channelConfiguration(4, False, True, True, False),
                   #'729Switch':channelConfiguration(5, False, True, True, False),
                   '110DPlist':channelConfiguration(6, True, True, True, False),
                   'camera':channelConfiguration(5, False, False, False, False),
                   #------------INTERNAL CHANNELS----------------------------------------#
                   'DiffCountTrigger':channelConfiguration(16, False, False, False, False),
                   'TimeResolvedCount':channelConfiguration(17, False, False, False, False),
                   
                   ###
                   #----- 18 ----- dds step to next value
                   #----- 19 ----- reset dds
                   ####
                   }
