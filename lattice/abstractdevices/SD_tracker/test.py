import labrad
from labrad.units import WithUnit
with labrad.connect() as cxn:
    tracker = cxn.sd_tracker
    lines = [('S+1/2D-3/2', WithUnit(226.091113788, 'MHz')), ('S+1/2D-1/2', WithUnit(226.590779307, 'MHz'))]
    tracker.set_measurements( lines)
    print tracker.get_measurements()
    print tracker.get_fit_parameters('linecenter')
    print tracker.get_fit_parameters('bfield')
    print tracker.get_current_lines()
    print tracker.get_current_line('S-1/2D+1/2')