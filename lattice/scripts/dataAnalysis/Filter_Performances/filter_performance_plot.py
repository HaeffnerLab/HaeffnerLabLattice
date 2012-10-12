import matplotlib
import numpy
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

figure = pyplot.figure()
figure.clf()

#lowpass filter
lowp_data = [
100.0, -95.0,
95.0, -95.0,
90.0, -94.0,
85.0, -93.0,
80.0, -92.0,
75.0, -90.0,
70.0, -89.0,
65.0, -87.0,
60.0, -85.0,
55.0, -84.0,
50.0, -83.0,
45.0, -82.0,
40.0, -82.0,
35.0, -81.0,
30.0, -80.0,
25.0, -79.0,
20.0, -78.0,
19.0, -78.0,
16.0, -84.0,
15.0, -90.0,
14.0, -81.0,
13.0, -72.0,
12.0, -64.0,
11.0, -58.0,
10.0, -51.0,
9.0, -43.0,
8.5, -38.0,
8.0, -34.0,
7.5, -28.0,
7.0, -21.0,
6.8, -18.0,
6.6, -14.0,
6.4, -11.0,
6.2, -8.0,
6.0, -6.0,
5.0, -4.0,
4.0, -5.0,
3.0, -4.0,
2.0, -4.0,
1.5, -5.0,
1.0, -5.0,
0.5, -5.0,
0.3, -5.0]

#isolated filter
iso_data = [
108.0, -61.0,
100.0, -58.0,
99.0, -59.0,
98.0, -59.0,
97.0, -58.0,
96.0, -58.0,
90.0, -58.0,
88.0, -61.0,
84.0, -67.0,
77.0, -69.0,
74.0, -64.0,
72.0, -71.0,
71.0, -79.0,
68.0, -80.0,
63.0, -79.0,
55.0, -60.0,
53.0, -57.0,
49.0, -65.0,
44.0, -72.0,
39.0, -75.0,
35.0, -80.0,
30.0, -85.0,
25.0, -91.0,
20.0, -97.0,
15.0, -104.0,
14.0, -106.0,
13.0, -109.0,
12.0, -112.0,
11.0, -97.0,
10.5, -99.0,
10.0, -102.0,
9.0, -105.0,
8.5, -107.0,
8.0, -108.0,
7.0, -109.0,
6.0, -112.0,
5.0, -114.0,
4.5, -118.0,
4.0, -118.0,
3.5, -120.0,
3.0, -120.0,
2.5, -121.0,
2.0, -122.0,
1.5, -122.0,
1.0, -122.0]

"""
i = 0
while i < len(data):
	if i % 2 == 0:
		freqs.append(data[i])
	else:
		dbm.append(data[i])
	i += 1
"""

lp = numpy.array(lowp_data)
lp = lp.reshape(-1, 2)
freqs, ampl_dbm = lp.transpose()

iso = numpy.array(iso_data)
iso = iso.reshape(-1, 2)
freqs2, ampl_dbm2 = iso.transpose()


# Set axes
pyplot.ylabel('dBm')
pyplot.ylim(-126, 0)
pyplot.xlabel('MHz')
pyplot.xlim(0, 110)
pyplot.suptitle('Filter Performances')

pyplot.plot(freqs, ampl_dbm, 'o-', label='Minicircuits 5 MHz Low Pass Filter')
pyplot.plot(freqs2, ampl_dbm2, 'go-', label='Isolated Filter')
pyplot.legend()
pyplot.show()