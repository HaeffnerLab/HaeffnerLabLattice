import test
import scan
a = test.Function()
b = test.ActionB()

#a.execute()
#a.setParameter('one',1)
#a.execute()
#print a.listParameters()

#repeat = scan.Repeat(a,50)
#repeat.setParameter('one',17)
#repeat.execute()
#print repeat.listParameters()

#OneDScan = scan.OneDScan(a,'one',0,100,10)
#OneDScan.setParameter('two',17)
#OneDScan.execute()
#print OneDScan.listParameters()

#TwoDScan = scan.TwoDScan(a,('one','two'),(0,0),(10,10),(5,5))
#TwoDScan.execute()
#print TwoDScan.listParameters()

#seq = scan.Sequence([a,b])
#print seq.listParameters()
#seq.setParameter('one',17)
#seq.setParameter('two',1317)
#seq.setParameter('a',6)
#seq.execute()

seq = scan.Sequence([a,b]) #sequence over two actions
repeat = scan.Repeat(seq,5) #repeat sequnce 5 times
OneDScan = scan.OneDScan(repeat,'one',0,10,10)
fullscan =  scan.Repeat(OneDScan,2)
fullscan.execute()

step[i] = ( foo , li )


excecuteSeq:
    for st in step:
	st[0].execute( *li )