def getAverageTotalCounts(counts):
    import numpy
    arr = counts.asarray
    totalcounts = numpy.transpose(arr)[1]
    averageTotalCounts = numpy.average(totalcounts)
    return averageTotalCounts
    
## sets the 
#def getAverageBackGroundCounts(counts):
#    import numpy
#    ###
#    pbox = client.connection.####
#    
#    #make sure paul's box trigger is on
#    
#    pbox.setmode(differential)
#    
#    pmt.getnextcounts(input)
#    pmt.average of the diff
#    box.setmode(normal)
#    
                       
                       
