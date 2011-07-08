def getAverageTotalCounts(counts):
    import numpy
    arr = counts.asarray
    totalcounts = numpy.transpose(arr)[1]
    averageTotalCounts = numpy.average(totalcounts)
    return averageTotalCounts
    
    