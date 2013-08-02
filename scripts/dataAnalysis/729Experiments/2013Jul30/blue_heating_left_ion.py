import labrad
from matplotlib import pyplot
import numpy as np

info = [(0, '0 mus heat, 0 mus delay', 
            [
#              ('2013Jul30', '1759_43',[]), #has unmatches time axis
            ('2013Jul30', '1820_04',[0,1,2,3, 58, 59, 60]),
            ('2013Jul30', '1839_30',[0,1,2,3,4]),
            ('2013Jul30', '1905_44',[0,1,2]),
             ]
         ),
        
        (0, '20 mus heat, 0 mus delay', 
            [
            ('2013Jul30', '1910_12',[0,1,2,3,101, 100, 99, 98, 97]),
#             ('2013Jul30', '1803_27',[]), #has unmatches time axis
            ('2013Jul30', '1826_31',[0,1,2,3]),
            ('2013Jul30', '1849_32',[0,1,2,3]),
             ]
         ),

        (0, '20 mus heat, 30 mus delay', 
            [
            ('2013Jul30', '1830_51',[0,1,2,3]),
#             ('2013Jul30', '1814_04',[]), #has unmatches time axis
#             ('2013Jul30', '1816_11',[]), #has unmatches time axis
            ('2013Jul30', '1854_00',[0,1,2,3]),
            ('2013Jul30', '1914_33',[0,1,2,3, 63, 64, 65]),
            ('2013Jul30', '1918_05',[0,1,2,3]),
             ]
         )        
        
        ]
 
cxn = labrad.connect()
dv = cxn.data_vault

#create the data structure in form [(times, rabi flop, points to remove)]

for ion_number, comment, datasets in info:
    all_data = []
    for date, datasetName, removePoints in datasets:
        dv.cd( ['','Experiments','Blue Heat RabiFlopping',date,datasetName])
        dv.open(1)
        dv_data = dv.get().asarray
        transpose = dv_data.transpose()
        times = transpose[0]
        flop = transpose[1:][ion_number]
        all_data.append((times, flop, removePoints))

    #find unique times
    times = [t[0] for t in all_data]
    combined = np.hstack(tuple(times))
    unique_times = np.unique(combined)
    print 'unique times size', unique_times.size
    
    averaging_array = np.empty((len(all_data), unique_times.size))
    averaging_array.fill(np.nan)
    for enum, (times,flop,remove_pts) in enumerate(all_data):
        times = np.delete(times, remove_pts)
        flop = np.delete(flop, remove_pts)
        mask = np.in1d(unique_times, times) #where current times match the unique times
        averaging_array[enum][mask] = flop
    
    masked_arr = np.ma.masked_array(averaging_array,np.isnan(averaging_array))
    if comment ==   '20 mus heat, 30 mus delay':
        print masked_arr
    averaged = np.mean(masked_arr, axis = 0)
    averaged = np.ma.filled(averaged, np.nan)
    validity = np.logical_not(np.isnan(averaged))#where we have averaged any values at all
    pyplot.plot(unique_times[validity], averaged[validity], 'o', label = comment)

pyplot.title('Left Ion', fontsize = 32)
pyplot.xlabel(u'Excitation Duration ($\mu s$)', fontsize = 32)
pyplot.ylabel('Excitation probability', fontsize = 32)
pyplot.ylim([0,1.0])
pyplot.legend(prop={'size':26})
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.grid(True, 'major')
pyplot.show()

# import numpy as np
# 
# arr = np.ma.array([1,2,3,4], mask = [False, False, False, True])
# print np.ma.average(arr)