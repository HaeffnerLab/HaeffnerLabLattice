# file: simcmds.tcl

# create the simulation script
vcd dumpfile isim.vcd
vcd dumpvars -m /clk_pll_100_in_200_out_tb -l 0
wave add /
run 50000ns
quit
