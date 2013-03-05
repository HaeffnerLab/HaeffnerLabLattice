library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.std_logic_arith.all;
use IEEE.std_logic_misc.all;
use IEEE.std_logic_unsigned.all;
use work.FRONTPANEL.all;
library UNISIM;
use UNISIM.VComponents.all;

entity pulser is

generic
  (
    C3_P0_MASK_SIZE           : integer := 4;
    C3_P0_DATA_PORT_SIZE      : integer := 32;
    C3_P1_MASK_SIZE           : integer := 4;
    C3_P1_DATA_PORT_SIZE      : integer := 32;
    C3_MEMCLK_PERIOD        : integer := 3200; 
                                       -- Memory data transfer clock period.
    C3_RST_ACT_LOW          : integer := 0; 
                                       -- # = 1 for active low reset,
                                       -- # = 0 for active high reset.
    C3_INPUT_CLK_TYPE       : string := "SINGLE_ENDED"; 
                                       -- input clock type DIFFERENTIAL or SINGLE_ENDED.
    C3_CALIB_SOFT_IP        : string := "TRUE"; 
                                       -- # = TRUE, Enables the soft calibration logic,
                                       -- # = FALSE, Disables the soft calibration logic.
    C3_SIMULATION           : string := "FALSE"; 
                                       -- # = TRUE, Simulating the design. Useful to reduce the simulation time,
                                       -- # = FALSE, Implementing the design.
    DEBUG_EN                : integer := 0; 
                                       -- # = 1, Enable debug signals/controls,
                                       --   = 0, Disable debug signals/controls.
    C3_MEM_ADDR_ORDER       : string := "ROW_BANK_COLUMN"; 
                                       -- The order in which user address is provided to the memory controller,
                                       -- ROW_BANK_COLUMN or BANK_ROW_COLUMN.
    C3_NUM_DQ_PINS          : integer := 16; 
                                       -- External memory data width.
    C3_MEM_ADDR_WIDTH       : integer := 13; 
                                       -- External memory address width.
    C3_MEM_BANKADDR_WIDTH   : integer := 3 
                                       -- External memory bank address width.
  );
  
	port (
		------ Opal Kelly Stuff -------
		hi_in     : in    STD_LOGIC_VECTOR(7 downto 0);
		hi_out    : out   STD_LOGIC_VECTOR(1 downto 0);
		hi_inout  : inout STD_LOGIC_VECTOR(15 downto 0);
		hi_muxsel : out   STD_LOGIC;
		hi_aa     : inout STD_LOGIC;
		i2c_sda   : out   STD_LOGIC;
		i2c_scl   : out   STD_LOGIC;
		------- clock in from Cypress. Normally configured at 100 MHz ------
		clk_in1      : in    STD_LOGIC;
		clk_in2      : in    STD_LOGIC;
		------- PMT input from the level translator. Note that the PMT pulse width is roughly 5-7 ns ----
		pmt_input : in 	STD_LOGIC;
		------- BNC in/out-----
		bnc_in : in STD_LOGIC_VECTOR (2 downto 0);
		bnc_out : out STD_LOGIC_VECTOR (3 downto 0);
		------- Logic In/Out ------
		logic_out: out STD_LOGIC_VECTOR (15 downto 0);
		logic_in:  in STD_LOGIC_VECTOR (3 downto 0);
		------- LED ------------------------
		led       : out   STD_LOGIC_VECTOR(7 downto 0);
		------- SDRAM protocol -------------
		mcb3_dram_dq                            : inout  std_logic_vector(C3_NUM_DQ_PINS-1 downto 0);
		mcb3_dram_a                             : out std_logic_vector(C3_MEM_ADDR_WIDTH-1 downto 0);
		mcb3_dram_ba                            : out std_logic_vector(C3_MEM_BANKADDR_WIDTH-1 downto 0);
		mcb3_dram_ras_n                         : out std_logic;
		mcb3_dram_cas_n                         : out std_logic;
		mcb3_dram_we_n                          : out std_logic;
		mcb3_dram_odt                           : out std_logic;
		mcb3_dram_cke                           : out std_logic;
		mcb3_dram_dm                            : out std_logic;
		mcb3_dram_udqs                          : inout  std_logic;
		mcb3_dram_udqs_n                        : inout  std_logic;
		mcb3_rzq                                : inout  std_logic;
		mcb3_zio                                : inout  std_logic;
		mcb3_dram_udm                           : out std_logic;
		mcb3_dram_dqs                           : inout  std_logic;
		mcb3_dram_dqs_n                         : inout  std_logic;
		mcb3_dram_ck                            : out std_logic;
		mcb3_dram_ck_n                          : out std_logic;
		mcb3_dram_cs_n									 : out std_logic; --- chip select pin ----
		
		------- TO DDS ---------------------
		dds_logic_data_out : out STD_LOGIC_VECTOR (15 downto 0);
		dds_logic_fifo_rd_clk: in STD_LOGIC;
		dds_logic_fifo_rd_en: in STD_LOGIC;
		dds_logic_fifo_empty: out STD_LOGIC;
		dds_logic_ram_reset: out STD_LOGIC;
		dds_logic_step_to_next_value: out STD_LOGIC;
		dds_logic_reset_dds_chip: out STD_LOGIC;
		dds_logic_ram_reset_manual: out STD_LOGIC;
		dds_logic_address : out STD_LOGIC_VECTOR (2 downto 0)
	);
end pulser;

architecture arch of pulser is

	---- SDRAM stuff ------
	
	component fifo_sdram_wr_w32_1024_r64_512 port (
	rst : in std_logic;
	wr_clk : in std_logic;
	rd_clk : in std_logic;
	din : in std_logic_vector(31 downto 0);
	wr_en : in std_logic;
	rd_en : in std_logic;
	dout : out std_logic_vector(63 downto 0);
	full : out std_logic;
	empty : out std_logic;
	valid : out std_logic;
	rd_data_count : out std_logic_vector(8 downto 0);
	wr_data_count : out std_logic_vector(9 downto 0));
end component;

component fifo_sdram_rd_w64_512_r16_2048 port (
	rst : in std_logic;
	wr_clk : in std_logic;
	rd_clk : in std_logic;
	din : in std_logic_vector(63 downto 0);
	wr_en : in std_logic;
	rd_en : in std_logic;
	dout : out std_logic_vector(15 downto 0);
	full : out std_logic;
	empty : out std_logic;
	valid : out std_logic;
	rd_data_count : out std_logic_vector(10 downto 0);
	wr_data_count : out std_logic_vector(8 downto 0));
end component;

 

component memc3_infrastructure is
    generic (
      C_RST_ACT_LOW        : integer;
      C_INPUT_CLK_TYPE     : string;
      C_CLKOUT0_DIVIDE     : integer;
      C_CLKOUT1_DIVIDE     : integer;
      C_CLKOUT2_DIVIDE     : integer;
      C_CLKOUT3_DIVIDE     : integer;
      C_CLKFBOUT_MULT      : integer;
      C_DIVCLK_DIVIDE      : integer;
      C_INCLK_PERIOD       : integer

      );
    port (
      sys_clk_p                              : in    std_logic;
      sys_clk_n                              : in    std_logic;
      sys_clk                                : in    std_logic;
      sys_rst_i                              : in    std_logic;
      clk0                                   : out   std_logic;
      rst0                                   : out   std_logic;
      async_rst                              : out   std_logic;
      sysclk_2x                              : out   std_logic;
      sysclk_2x_180                          : out   std_logic;
      pll_ce_0                               : out   std_logic;
      pll_ce_90                              : out   std_logic;
      pll_lock                               : out   std_logic;
      mcb_drp_clk                            : out   std_logic

      );
  end component;


component memc3_wrapper is
    generic (
      C_MEMCLK_PERIOD      : integer;
      C_CALIB_SOFT_IP      : string;
      C_SIMULATION         : string;
      C_P0_MASK_SIZE       : integer;
      C_P0_DATA_PORT_SIZE   : integer;
      C_P1_MASK_SIZE       : integer;
      C_P1_DATA_PORT_SIZE   : integer;
      C_ARB_NUM_TIME_SLOTS   : integer;
      C_ARB_TIME_SLOT_0    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_1    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_2    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_3    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_4    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_5    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_6    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_7    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_8    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_9    : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_10   : bit_vector(2 downto 0);
      C_ARB_TIME_SLOT_11   : bit_vector(2 downto 0);
      C_MEM_TRAS           : integer;
      C_MEM_TRCD           : integer;
      C_MEM_TREFI          : integer;
      C_MEM_TRFC           : integer;
      C_MEM_TRP            : integer;
      C_MEM_TWR            : integer;
      C_MEM_TRTP           : integer;
      C_MEM_TWTR           : integer;
      C_MEM_ADDR_ORDER     : string;
      C_NUM_DQ_PINS        : integer;
      C_MEM_TYPE           : string;
      C_MEM_DENSITY        : string;
      C_MEM_BURST_LEN      : integer;
      C_MEM_CAS_LATENCY    : integer;
      C_MEM_ADDR_WIDTH     : integer;
      C_MEM_BANKADDR_WIDTH   : integer;
      C_MEM_NUM_COL_BITS   : integer;
      C_MEM_DDR1_2_ODS     : string;
      C_MEM_DDR2_RTT       : string;
      C_MEM_DDR2_DIFF_DQS_EN   : string;
      C_MEM_DDR2_3_PA_SR   : string;
      C_MEM_DDR2_3_HIGH_TEMP_SR   : string;
      C_MEM_DDR3_CAS_LATENCY   : integer;
      C_MEM_DDR3_ODS       : string;
      C_MEM_DDR3_RTT       : string;
      C_MEM_DDR3_CAS_WR_LATENCY   : integer;
      C_MEM_DDR3_AUTO_SR   : string;
      C_MEM_DDR3_DYN_WRT_ODT   : string;
      C_MEM_MOBILE_PA_SR   : string;
      C_MEM_MDDR_ODS       : string;
      C_MC_CALIB_BYPASS    : string;
      C_MC_CALIBRATION_MODE   : string;
      C_MC_CALIBRATION_DELAY   : string;
      C_SKIP_IN_TERM_CAL   : integer;
      C_SKIP_DYNAMIC_CAL   : integer;
      C_LDQSP_TAP_DELAY_VAL   : integer;
      C_LDQSN_TAP_DELAY_VAL   : integer;
      C_UDQSP_TAP_DELAY_VAL   : integer;
      C_UDQSN_TAP_DELAY_VAL   : integer;
      C_DQ0_TAP_DELAY_VAL   : integer;
      C_DQ1_TAP_DELAY_VAL   : integer;
      C_DQ2_TAP_DELAY_VAL   : integer;
      C_DQ3_TAP_DELAY_VAL   : integer;
      C_DQ4_TAP_DELAY_VAL   : integer;
      C_DQ5_TAP_DELAY_VAL   : integer;
      C_DQ6_TAP_DELAY_VAL   : integer;
      C_DQ7_TAP_DELAY_VAL   : integer;
      C_DQ8_TAP_DELAY_VAL   : integer;
      C_DQ9_TAP_DELAY_VAL   : integer;
      C_DQ10_TAP_DELAY_VAL   : integer;
      C_DQ11_TAP_DELAY_VAL   : integer;
      C_DQ12_TAP_DELAY_VAL   : integer;
      C_DQ13_TAP_DELAY_VAL   : integer;
      C_DQ14_TAP_DELAY_VAL   : integer;
      C_DQ15_TAP_DELAY_VAL   : integer
      );
    port (
      mcb3_dram_dq                           : inout  std_logic_vector((C_NUM_DQ_PINS-1) downto 0);
      mcb3_dram_a                            : out  std_logic_vector((C_MEM_ADDR_WIDTH-1) downto 0);
      mcb3_dram_ba                           : out  std_logic_vector((C_MEM_BANKADDR_WIDTH-1) downto 0);
      mcb3_dram_ras_n                        : out  std_logic;
      mcb3_dram_cas_n                        : out  std_logic;
      mcb3_dram_we_n                         : out  std_logic;
      mcb3_dram_odt                          : out  std_logic;
      mcb3_dram_cke                          : out  std_logic;
      mcb3_dram_dm                           : out  std_logic;
      mcb3_dram_udqs                         : inout  std_logic;
      mcb3_dram_udqs_n                       : inout  std_logic;
      mcb3_rzq                               : inout  std_logic;
      mcb3_zio                               : inout  std_logic;
      mcb3_dram_udm                          : out  std_logic;
      calib_done                             : out  std_logic;
      async_rst                              : in  std_logic;
      sysclk_2x                              : in  std_logic;
      sysclk_2x_180                          : in  std_logic;
      pll_ce_0                               : in  std_logic;
      pll_ce_90                              : in  std_logic;
      pll_lock                               : in  std_logic;
      mcb_drp_clk                            : in  std_logic;
      mcb3_dram_dqs                          : inout  std_logic;
      mcb3_dram_dqs_n                        : inout  std_logic;
      mcb3_dram_ck                           : out  std_logic;
      mcb3_dram_ck_n                         : out  std_logic;
      p0_cmd_clk                            : in std_logic;
      p0_cmd_en                             : in std_logic;
      p0_cmd_instr                          : in std_logic_vector(2 downto 0);
      p0_cmd_bl                             : in std_logic_vector(5 downto 0);
      p0_cmd_byte_addr                      : in std_logic_vector(29 downto 0);
      p0_cmd_empty                          : out std_logic;
      p0_cmd_full                           : out std_logic;
      p0_wr_clk                             : in std_logic;
      p0_wr_en                              : in std_logic;
      p0_wr_mask                            : in std_logic_vector(C_P0_MASK_SIZE - 1 downto 0);
      p0_wr_data                            : in std_logic_vector(C_P0_DATA_PORT_SIZE - 1 downto 0);
      p0_wr_full                            : out std_logic;
      p0_wr_empty                           : out std_logic;
      p0_wr_count                           : out std_logic_vector(6 downto 0);
      p0_wr_underrun                        : out std_logic;
      p0_wr_error                           : out std_logic;
      p0_rd_clk                             : in std_logic;
      p0_rd_en                              : in std_logic;
      p0_rd_data                            : out std_logic_vector(C_P0_DATA_PORT_SIZE - 1 downto 0);
      p0_rd_full                            : out std_logic;
      p0_rd_empty                           : out std_logic;
      p0_rd_count                           : out std_logic_vector(6 downto 0);
      p0_rd_overflow                        : out std_logic;
      p0_rd_error                           : out std_logic;
      selfrefresh_enter                     : in std_logic;
      selfrefresh_mode                      : out std_logic

      );
  end component;
  
	component ddr2_test port (
		clk: in std_logic;
		reset: in std_logic;
		writes_en: in std_logic;
		reads_en: in std_logic;
		calib_done: in std_logic; 
		ram_full: out STD_LOGIC;

		ib_re: out std_logic;
		ib_data: in std_logic_vector(63 downto 0);
		ib_count: in std_logic_vector(8 downto 0);
		ib_valid: in std_logic;
		ib_empty: in std_logic;

		ob_we: out std_logic;
		ob_data: out std_logic_vector (63 downto 0);
		ob_count: in std_logic_vector(8 downto 0);
	
		p0_rd_en_o: out std_logic; 
		p0_rd_empty: in std_logic;
		p0_rd_data: in std_logic_vector(31 downto 0);
	
		p0_cmd_full: in std_logic;
		p0_cmd_en: out std_logic;
		p0_cmd_instr: out std_logic_vector(2 downto 0);
		p0_cmd_byte_addr: out std_logic_vector (29 downto 0);
		p0_cmd_bl_o: out std_logic_vector (5 downto 0); 
		p0_wr_full: in std_logic;
		p0_wr_en: out std_logic;
		p0_wr_data: out std_logic_vector (31 downto 0);
		p0_wr_mask: out std_logic_vector (3 downto 0));
	end component;
	
	---- clocking pll component -----
	component clk_pll port (
	-- Clock in ports
		CLK_IN1           : in     std_logic;
   -- Clock out ports
		CLK_OUT1          : out    std_logic;
		CLK_OUT2          : out    std_logic;
		CLK_OUT3          : out    std_logic);
	end component;
	
	---- fifo for dds ----
	
	component fifo_dds_w16_2048_r16_2048 PORT (
		rst : IN STD_LOGIC;
		wr_clk : IN STD_LOGIC;
		rd_clk : IN STD_LOGIC;
		din : IN STD_LOGIC_VECTOR(15 DOWNTO 0);
		wr_en : IN STD_LOGIC;
		rd_en : IN STD_LOGIC;
		dout : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
		full : OUT STD_LOGIC;
		empty : OUT STD_LOGIC;
		wr_data_count: OUT STD_LOGIC_VECTOR(10 downto 0));
	end component;
	
	
	----- block ram to store the pulses ---------------------------------------------------------------------
	----- The pulse data is first written into fifo (below). Then the fifo will transfer the data to ram. ----
	
	component ram_pulser PORT (
		clka : IN STD_LOGIC;
		wea : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
		addra : IN STD_LOGIC_VECTOR(13 DOWNTO 0);
		dina : IN STD_LOGIC_VECTOR(63 DOWNTO 0);
		clkb : IN STD_LOGIC;
		addrb : IN STD_LOGIC_VECTOR(13 DOWNTO 0);
		doutb : OUT STD_LOGIC_VECTOR(63 DOWNTO 0));
	end component;
	
	------ fifo to from pc to ram to store pulse ----
	
	component fifo_pulse_seq_w16_1024_r64_256 PORT (
		rst : IN STD_LOGIC;
		wr_clk : IN STD_LOGIC;
		rd_clk : IN STD_LOGIC;
		din : IN STD_LOGIC_VECTOR(15 DOWNTO 0);
		wr_en : IN STD_LOGIC;
		rd_en : IN STD_LOGIC;
		dout : OUT STD_LOGIC_VECTOR(63 DOWNTO 0);
		full : OUT STD_LOGIC;
		empty : OUT STD_LOGIC;
		rd_data_count : OUT STD_LOGIC_VECTOR(7 DOWNTO 0));
	end component;
	
	-------- pmt fifo for normal counting and readout ---------
	
	component fifo_pmt_w32_1024_r16_2048 PORT (
		rst : IN STD_LOGIC;
		wr_clk : IN STD_LOGIC;
		rd_clk : IN STD_LOGIC;
		din : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
		wr_en : IN STD_LOGIC;
		rd_en : IN STD_LOGIC;
		dout : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
		full : OUT STD_LOGIC;
		empty : OUT STD_LOGIC;
		rd_data_count : OUT STD_LOGIC_VECTOR(10 DOWNTO 0));
	end component;
	
	-- constants for sdram stuff --
	
	constant C3_CLKOUT0_DIVIDE       : integer := 1; 
   constant C3_CLKOUT1_DIVIDE       : integer := 1; 
   constant C3_CLKOUT2_DIVIDE       : integer := 4; 
   constant C3_CLKOUT3_DIVIDE       : integer := 8; 
   constant C3_CLKFBOUT_MULT        : integer := 25; 
   constant C3_DIVCLK_DIVIDE        : integer := 4; 
   constant C3_INCLK_PERIOD         : integer := ((C3_MEMCLK_PERIOD * C3_CLKFBOUT_MULT) / (C3_DIVCLK_DIVIDE * C3_CLKOUT0_DIVIDE * 2)); 
   constant C3_ARB_NUM_TIME_SLOTS   : integer := 12; 
   constant C3_ARB_TIME_SLOT_0      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_1      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_2      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_3      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_4      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_5      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_6      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_7      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_8      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_9      : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_10     : bit_vector(2 downto 0) := o"0"; 
   constant C3_ARB_TIME_SLOT_11     : bit_vector(2 downto 0) := o"0"; 
   constant C3_MEM_TRAS             : integer := 40000; 
   constant C3_MEM_TRCD             : integer := 15000; 
   constant C3_MEM_TREFI            : integer := 7800000; 
   constant C3_MEM_TRFC             : integer := 127500; 
   constant C3_MEM_TRP              : integer := 15000; 
   constant C3_MEM_TWR              : integer := 15000; 
   constant C3_MEM_TRTP             : integer := 7500; 
   constant C3_MEM_TWTR             : integer := 7500; 
   constant C3_MEM_TYPE             : string := "DDR2"; 
   constant C3_MEM_DENSITY          : string := "1Gb"; 
   constant C3_MEM_BURST_LEN        : integer := 4; 
   constant C3_MEM_CAS_LATENCY      : integer := 5; 
   constant C3_MEM_NUM_COL_BITS     : integer := 10; 
   constant C3_MEM_DDR1_2_ODS       : string := "FULL"; 
   constant C3_MEM_DDR2_RTT         : string := "50OHMS"; 
   constant C3_MEM_DDR2_DIFF_DQS_EN  : string := "YES"; 
   constant C3_MEM_DDR2_3_PA_SR     : string := "FULL"; 
   constant C3_MEM_DDR2_3_HIGH_TEMP_SR  : string := "NORMAL"; 
   constant C3_MEM_DDR3_CAS_LATENCY  : integer := 6; 
   constant C3_MEM_DDR3_ODS         : string := "DIV6"; 
   constant C3_MEM_DDR3_RTT         : string := "DIV2"; 
   constant C3_MEM_DDR3_CAS_WR_LATENCY  : integer := 5; 
   constant C3_MEM_DDR3_AUTO_SR     : string := "ENABLED"; 
   constant C3_MEM_DDR3_DYN_WRT_ODT  : string := "OFF"; 
   constant C3_MEM_MOBILE_PA_SR     : string := "FULL"; 
   constant C3_MEM_MDDR_ODS         : string := "FULL"; 
   constant C3_MC_CALIB_BYPASS      : string := "NO"; 
   constant C3_MC_CALIBRATION_MODE  : string := "CALIBRATION"; 
   constant C3_MC_CALIBRATION_DELAY  : string := "HALF"; 
   constant C3_SKIP_IN_TERM_CAL     : integer := 0; 
   constant C3_SKIP_DYNAMIC_CAL     : integer := 0; 
   constant C3_LDQSP_TAP_DELAY_VAL  : integer := 0; 
   constant C3_LDQSN_TAP_DELAY_VAL  : integer := 0; 
   constant C3_UDQSP_TAP_DELAY_VAL  : integer := 0; 
   constant C3_UDQSN_TAP_DELAY_VAL  : integer := 0; 
   constant C3_DQ0_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ1_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ2_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ3_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ4_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ5_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ6_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ7_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ8_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ9_TAP_DELAY_VAL    : integer := 0; 
   constant C3_DQ10_TAP_DELAY_VAL   : integer := 0; 
   constant C3_DQ11_TAP_DELAY_VAL   : integer := 0; 
   constant C3_DQ12_TAP_DELAY_VAL   : integer := 0; 
   constant C3_DQ13_TAP_DELAY_VAL   : integer := 0; 
   constant C3_DQ14_TAP_DELAY_VAL   : integer := 0; 
   constant C3_DQ15_TAP_DELAY_VAL   : integer := 0; 
   constant C3_SMALL_DEVICE         : string := "FALSE"; -- The parameter is set to TRUE for all packages of xc6slx9 device
                                                         -- as most of them cannot fit the complete example design when the
                                                         -- Chip scope modules are enabled

  signal  c3_sys_clk                               : std_logic;
  signal  c3_async_rst                             : std_logic;
  signal  c3_sysclk_2x                             : std_logic;
  signal  c3_sysclk_2x_180                         : std_logic;
  signal  c3_pll_ce_0                              : std_logic;
  signal  c3_pll_ce_90                             : std_logic;
  signal  c3_pll_lock                              : std_logic;
  signal  c3_mcb_drp_clk                           : std_logic;
  signal  c3_cmp_error                             : std_logic;
  signal  c3_cmp_data_valid                        : std_logic;
  signal  c3_vio_modify_enable                     : std_logic;
  signal  c3_error_status                          : std_logic_vector(127 downto 0);
  signal  c3_vio_data_mode_value                   : std_logic_vector(2 downto 0);
  signal  c3_vio_addr_mode_value                   : std_logic_vector(2 downto 0);
  signal  c3_cmp_data                              : std_logic_vector(31 downto 0);
  signal  c3_selfrefresh_enter                     : std_logic;
  signal  c3_selfrefresh_mode                      : std_logic;
  
  signal  c3_clk0		: std_logic;
  signal  c3_rst0		: std_logic;
  signal  c3_p0_cmd_full		: std_logic;
  signal  c3_p0_cmd_en		: std_logic;
  signal  c3_p0_cmd_instr : std_logic_vector(2 downto 0);
  signal  c3_p0_cmd_byte_addr : std_logic_vector(29 downto 0);
  signal  c3_p0_cmd_bl : std_logic_vector(5 downto 0);
  signal  c3_p0_wr_en	: std_logic;
  signal  c3_p0_wr_full	: std_logic;
  signal  c3_p0_wr_data : std_logic_vector(C3_P0_DATA_PORT_SIZE-1 downto 0);
  signal  c3_p0_wr_mask : std_logic_vector(C3_P0_MASK_SIZE-1 downto 0);
  signal  c3_sys_clk_p	: std_logic;
  signal  c3_calib_done		: std_logic;
  signal  c3_p0_rd_en  : std_logic;
  signal  c3_p0_rd_empty  : std_logic;
  signal  c3_p0_rd_data  : std_logic_vector(C3_P0_DATA_PORT_SIZE-1 downto 0);
  
  signal  c3_sys_clk_n		: std_logic;
  signal  c3_sys_rst_i		: std_logic;
  signal  c3_p0_cmd_clk		: std_logic;
  signal  c3_p0_cmd_empty		: std_logic;
  signal  c3_p0_wr_clk		: std_logic;
  signal  c3_p0_wr_empty		: std_logic;
  signal  c3_p0_wr_underrun		: std_logic;
  signal  c3_p0_wr_count  : std_logic_vector(6 downto 0);
  signal  c3_p0_wr_error		: std_logic;
  signal  c3_p0_rd_clk		: std_logic;
  signal  c3_p0_rd_full		: std_logic;
  signal  c3_p0_rd_count  : std_logic_vector(6 downto 0);
  signal  c3_p0_rd_overflow : std_logic;
  signal  c3_p0_rd_error : std_logic;
	
	
	
	-- Target interface bus:
	signal ti_clk    : STD_LOGIC;
	signal ok1       : STD_LOGIC_VECTOR(30 downto 0);
	signal ok2       : STD_LOGIC_VECTOR(16 downto 0);
	signal ok2s      : STD_LOGIC_VECTOR(17*8-1 downto 0);

  -- Endpoint connections:
	------ configuration register ------
	signal ep00wire        : STD_LOGIC_VECTOR(15 downto 0):="0000000000000000";
	------ normal pmt measure period -------
	signal ep01wire        : STD_LOGIC_VECTOR(15 downto 0);
	
	------ Manual overwrite of the output logic ------
	------ Because there are 4 possible states for each channel of the logic out (there are
	------ always on, always off, follow pulse, follow pulse with inverted), we need 2 bits of
	------ information to store.
	
	signal ep02wire		  : STD_LOGIC_VECTOR(15 downto 0);
	signal ep03wire		  : STD_LOGIC_VECTOR(15 downto 0);
	------ DDS channel ---------------------
	signal ep04wire		  : STD_LOGIC_VECTOR(15 downto 0);
	------ Number of loops wanted in the infinite loop ---------------------
	signal ep05wire		  : STD_LOGIC_VECTOR(15 downto 0);
	------ number of us delay in the line triggering ---------------------
	signal ep06wire		  : STD_LOGIC_VECTOR(15 downto 0):="0000000000000000";
	------ epwire for sdram testing ------
	signal ep07wire		  : STD_LOGIC_VECTOR(15 downto 0);
	
	------ output data to PC ------
	signal ep21wire		  : STD_LOGIC_VECTOR(15 downto 0):="0000000000000000";
	------ store number of photon data written to sdram -------
	signal ep22wire		  : STD_LOGIC_VECTOR(15 downto 0):="0000000000000000";
	signal ep23wire		  : STD_LOGIC_VECTOR(15 downto 0):="0000000000000000";
	------ Trigger in ------
	signal ep40wire        : STD_LOGIC_VECTOR(15 downto 0);

	----- These are for pipe logic ----
	
	signal pipe_in_write   : STD_LOGIC;
	signal pipe_in_ready   : STD_LOGIC;
	signal pipe_in_data    : STD_LOGIC_VECTOR(15 downto 0);
	
	signal pipe_in_write_dds   : STD_LOGIC;
	signal pipe_in_ready_dds   : STD_LOGIC;
	signal pipe_in_data_dds    : STD_LOGIC_VECTOR(15 downto 0);
	
	signal time_resolved_pipe_out_read   : STD_LOGIC;
	signal time_resolved_pipe_out_valid  : STD_LOGIC;
	signal time_resolved_pipe_out_data   : STD_LOGIC_VECTOR(15 downto 0);
	
	signal normal_pmt_pipe_out_read   : STD_LOGIC;
	signal normal_pmt_pipe_out_valid  : STD_LOGIC;
	signal normal_pmt_pipe_out_data   : STD_LOGIC_VECTOR(15 downto 0);
	
	----- pipe for sdram testing -----
	
	signal        pipe_in_sdram_start: std_logic;
	signal        pipe_in_sdram_done: std_logic;
	signal        pipe_in_sdram_read: std_logic;
	signal        pipe_in_sdram_data: std_logic_vector(63 downto 0);
	signal        pipe_in_sdram_count: std_logic_vector(8 downto 0);
	signal        pipe_in_sdram_valid: std_logic;
	signal        pipe_in_sdram_empty: std_logic;
	
	signal        pipe_out_sdram_start: std_logic;
	signal        pipe_out_sdram_done: std_logic;
	signal        pipe_out_sdram_write: std_logic;
	signal        pipe_out_sdram_data: std_logic_vector(63 downto 0);
	signal        pipe_out_sdram_count: std_logic_vector(8 downto 0);
	signal        pipe_out_sdram_full: std_logic;
	
	signal        pi0_ep_write, po0_ep_read: std_logic;
	signal        pi0_ep_dataout, po0_ep_datain: std_logic_vector(15 downto 0);
	
	signal		  ram_full_flag: std_logic;
	
	
	
	signal bs_in, bs_out   : STD_LOGIC;
	signal bs_in_dds, bs_out_dds   : STD_LOGIC;
	
	--- CLOCKs -----

	--- clk 100 MHz from PLL.
	signal clk_100         : STD_LOGIC;
	--- clk 200 MHz from PLL to sample the input PMT signal. Any slower clock will miss the pulse ---
	signal clk_200         : STD_LOGIC;
	--- clk 20 MHz from PLL. Not used for anything right now ----
	signal clk_20          : STD_LOGIC; 
	--- slow clock at 1 MHz self-generated ---
	signal clk_1			  : STD_LOGIC;

	---- fifo photon signal ----
	
	signal   fifo_photon_rst 		: STD_LOGIC;
	signal	fifo_photon_wr_clk	: STD_LOGIC;
	signal	fifo_photon_din		: STD_LOGIC_VECTOR(31 downto 0);
	signal	fifo_photon_wr_en		: STD_LOGIC;
	signal	fifo_photon_full		: STD_LOGIC;
	signal	fifo_photon_empty		: STD_LOGIC;
	signal   fifo_photon_rd_data_count: STD_LOGIC_VECTOR(15 downto 0);
	signal   photon_time_tag      : STD_LOGIC_VECTOR(31 downto 0);
	
	---- fifo pulser signal ----
	
	signal   fifo_pulser_rst 		: STD_LOGIC;
	signal	fifo_pulser_rd_clk	: STD_LOGIC;
	signal	fifo_pulser_rd_en		: STD_LOGIC;
	signal	fifo_pulser_dout		: STD_LOGIC_VECTOR(63 downto 0);
	signal	fifo_pulser_full		: STD_LOGIC;
	signal	fifo_pulser_empty		: STD_LOGIC;
	signal   fifo_pulser_rd_data_count: STD_LOGIC_VECTOR(7 downto 0);
	
		---- dds pulser signal ----
	
	signal   fifo_dds_rst 		: STD_LOGIC;
	signal	fifo_dds_rd_clk	: STD_LOGIC;
	signal   fifo_dds_rd_clk_temp: STD_LOGIC;
	signal	fifo_dds_rd_en		: STD_LOGIC;
	signal	fifo_dds_dout		: STD_LOGIC_VECTOR(15 downto 0);
	signal	fifo_dds_full		: STD_LOGIC;
	signal	fifo_dds_empty		: STD_LOGIC;
	signal	fifo_dds_wr_data_count		: STD_LOGIC_vector(10 downto 0);
	signal   dds_ram_reset     : STD_LOGIC;
	
	----- main signal route -----
	signal 	master_counter_hi_bit: STD_LOGIC_VECTOR (29 downto 0); ---- this one is the counter for the pulser
	signal 	master_counter_low_bit: STD_LOGIC_VECTOR (1 downto 0); ---- this one is the sub counter for the photon data. The combined is 32 bit
	----- These two are the time variable of the evolution of the pulses.
	----- Due to the limitation of the integer size in VHDL, the number has to
	----- be divided into two separated numbers.
	signal 	master_counter_hi_int: integer range 0 to 1073741824 := 0;
	signal	master_counter_low_int: integer range 0 to 3 := 0;
	
	----- logic signal ------------------------------
	----- This is the channels for the pulse sequence
	
	signal 	master_logic			:STD_LOGIC_VECTOR (31 downto 0);
	
	----- pmt signal --------------------------------------------

	signal 	pmt_synced				: STD_LOGIC; ------------
	
	----- pulser ram ------
	
	signal	pulser_ram_clka        		: STD_LOGIC;
	signal	pulser_ram_wea 				: STD_LOGIC_VECTOR(0 DOWNTO 0);
	signal	pulser_ram_addra 				: STD_LOGIC_VECTOR(13 DOWNTO 0);
	signal	pulser_ram_dina 				: STD_LOGIC_VECTOR(63 DOWNTO 0);
	signal	pulser_ram_clkb 				: STD_LOGIC;
	signal	pulser_ram_addrb 				: STD_LOGIC_VECTOR(13 DOWNTO 0);
	signal	pulser_ram_doutb 				: STD_LOGIC_VECTOR(63 DOWNTO 0);
	
	------ This is the total number of sequence completed in the infinite loop mode of the pulser
	signal   seq_count_bit					: STD_LOGIC_VECTOR(15 downto 0);
	
	----- various flag -----
	signal   pulser_counter_reset			: STD_LOGIC; ----'0' = reset. '1' = run
	signal   pulser_ram_reset			   : STD_LOGIC; ----'1' = reset pulser ram. '0' = normal operating state
	signal	pulser_infinite_loop			: STD_LOGIC; ----'1' = infinite loop. '0' = single shot
	signal	pulser_start_bit				: STD_LOGIC; ----'1' = run sequence. '0' = pause sequence
	signal	pulser_sequence_done			: STD_LOGIC; ----'1' = sequence is done. '0' = seq is not yet done. In infinite mode it will always be '0'
	signal	pulser_flag_register			: STD_LOGIC_VECTOR (15 downto 0);---- this vector is to combine all above for convenience.
	
	--====== NORMAL PMT ========--
	-- FIFO --
	signal   normal_pmt_rd_data_count: STD_LOGIC_VECTOR (10 DOWNTO 0);
	signal   normal_pmt_full: STD_LOGIC;
	signal   normal_pmt_fifo_reset: STD_LOGIC;
	signal   normal_pmt_fifo_data: STD_LOGIC_VECTOR (31 DOWNTO 0);
	signal   normal_pmt_empty: STD_LOGIC;
	signal   normal_pmt_wr_clk: STD_LOGIC:='0';
	signal   normal_pmt_wr_en: STD_LOGIC:='0';
	signal   normal_pmt_block_aval: STD_LOGIC:= '0';
	
	-- auto mode parameter --
	signal   normal_pmt_count_period : INTEGER RANGE 0 TO 65535:=1000; --- normal pmt period in ms ---
	signal   normal_pmt_auto_count_clk : STD_LOGIC:='0';
	signal   normal_pmt_count_trigger : STD_LOGIC := '0';
	
	-- PMT data --
	signal   pmt_count: INTEGER RANGE 0 TO 2147483647:=0;
	signal   pmt_count_reset: STD_LOGIC;
	signal   pmt_sampled: STD_LOGIC;
	
	--====== READOUT PMT ========--
	--FIFO--
	signal   readout_count_rd_data_count: STD_LOGIC_VECTOR (10 DOWNTO 0);
	signal   readout_pmt_full: STD_LOGIC;
	signal   readout_count_fifo_reset: STD_LOGIC;
	signal   readout_count_fifo_data: STD_LOGIC_VECTOR (31 DOWNTO 0);
	signal   readout_pmt_empty: STD_LOGIC;
	signal   readout_count_wr_clk: STD_LOGIC:='0';
	signal   readout_count_wr_en: STD_LOGIC:='0';
	signal   readout_count_pipe_out_read: STD_LOGIC := '0';
	signal   readout_count_pipe_out_valid: STD_LOGIC;
	signal   readout_count_pipe_out_data: STD_LOGIC_VECTOR (15 DOWNTO 0);
	--DATA--
	signal	pmt_readout_count: INTEGER RANGE 0 TO 2147483647:=0;
	signal	readout_should_count : STD_LOGIC := '0';
	
	
	----- line triggering -----
	signal line_triggering_enabled: STD_LOGIC := '0'; ----- 1 means trigger with line
	signal line_triggering_pulse: STD_LOGIC := '0'; ------ line triggering pulse from some input
	signal line_triggering_conditioned: STD_LOGIC:= '0'; ----- conditioning of the 60 hz input
	
	--------------------aux logic for 	-----


begin


-----------------------------------------------------------------------------
--------------- SDRAM stuff -----------------------------------

c3_sys_clk <= '0';
c3_selfrefresh_enter <= '0';
c3_sys_clk_p <= '0';
c3_sys_clk_n <= '0';
mcb3_dram_cs_n <= '0';

c3_sys_rst_i <= '0';

ep23wire(13 downto 0) <= c3_p0_cmd_byte_addr(29 downto 16);
ep23wire(15) <= ram_full_flag;
ep22wire <= c3_p0_cmd_byte_addr(15 downto 0);

ddr2 : ddr2_test

port map (
		clk => c3_clk0,
		reset => ep07wire(2) or c3_rst0,
		writes_en => ep07wire(1),
		reads_en => ep07wire(0),
		calib_done => c3_calib_done,
		ram_full => ram_full_flag,

		ib_re => pipe_in_sdram_read,
		ib_data => pipe_in_sdram_data,
		ib_count => pipe_in_sdram_count,
		ib_valid => pipe_in_sdram_valid,
		ib_empty => pipe_in_sdram_empty,

		ob_we => pipe_out_sdram_write,
		ob_data => pipe_out_sdram_data,
		ob_count => pipe_out_sdram_count,
	
		p0_rd_en_o => c3_p0_rd_en,
		p0_rd_empty => c3_p0_rd_empty,
		p0_rd_data => c3_p0_rd_data,
	
		p0_cmd_full => c3_p0_cmd_full,
		p0_cmd_en => c3_p0_cmd_en,
		p0_cmd_instr => c3_p0_cmd_instr,
		p0_cmd_byte_addr => c3_p0_cmd_byte_addr,
		p0_cmd_bl_o => c3_p0_cmd_bl, 
		p0_wr_full => c3_p0_wr_full,
		p0_wr_en => c3_p0_wr_en,
		p0_wr_data => c3_p0_wr_data,
		p0_wr_mask => c3_p0_wr_mask);

memc3_infrastructure_inst : memc3_infrastructure

generic map
 (
   C_RST_ACT_LOW                     => C3_RST_ACT_LOW,
   C_INPUT_CLK_TYPE                  => C3_INPUT_CLK_TYPE,
   C_CLKOUT0_DIVIDE                  => C3_CLKOUT0_DIVIDE,
   C_CLKOUT1_DIVIDE                  => C3_CLKOUT1_DIVIDE,
   C_CLKOUT2_DIVIDE                  => C3_CLKOUT2_DIVIDE,
   C_CLKOUT3_DIVIDE                  => C3_CLKOUT3_DIVIDE,
   C_CLKFBOUT_MULT                   => C3_CLKFBOUT_MULT,
   C_DIVCLK_DIVIDE                   => C3_DIVCLK_DIVIDE,
   C_INCLK_PERIOD                    => C3_INCLK_PERIOD
   )
port map
 (
   sys_clk_p                       => c3_sys_clk_p,
   sys_clk_n                       => c3_sys_clk_n,
   sys_clk                         => clk_in2,
   sys_rst_i                       => c3_sys_rst_i,
   clk0                            => c3_clk0,
   rst0                            => c3_rst0,
   async_rst                       => c3_async_rst,
   sysclk_2x                       => c3_sysclk_2x,
   sysclk_2x_180                   => c3_sysclk_2x_180,
   pll_ce_0                        => c3_pll_ce_0,
   pll_ce_90                       => c3_pll_ce_90,
   pll_lock                        => c3_pll_lock,
   mcb_drp_clk                     => c3_mcb_drp_clk
   );


-- wrapper instantiation
 memc3_wrapper_inst : memc3_wrapper

generic map
 (
   C_MEMCLK_PERIOD                   => C3_MEMCLK_PERIOD,
   C_CALIB_SOFT_IP                   => C3_CALIB_SOFT_IP,
   C_SIMULATION                      => C3_SIMULATION,
   C_P0_MASK_SIZE                    => C3_P0_MASK_SIZE,
   C_P0_DATA_PORT_SIZE               => C3_P0_DATA_PORT_SIZE,
   C_P1_MASK_SIZE                    => C3_P1_MASK_SIZE,
   C_P1_DATA_PORT_SIZE               => C3_P1_DATA_PORT_SIZE,
   C_ARB_NUM_TIME_SLOTS              => C3_ARB_NUM_TIME_SLOTS,
   C_ARB_TIME_SLOT_0                 => C3_ARB_TIME_SLOT_0,
   C_ARB_TIME_SLOT_1                 => C3_ARB_TIME_SLOT_1,
   C_ARB_TIME_SLOT_2                 => C3_ARB_TIME_SLOT_2,
   C_ARB_TIME_SLOT_3                 => C3_ARB_TIME_SLOT_3,
   C_ARB_TIME_SLOT_4                 => C3_ARB_TIME_SLOT_4,
   C_ARB_TIME_SLOT_5                 => C3_ARB_TIME_SLOT_5,
   C_ARB_TIME_SLOT_6                 => C3_ARB_TIME_SLOT_6,
   C_ARB_TIME_SLOT_7                 => C3_ARB_TIME_SLOT_7,
   C_ARB_TIME_SLOT_8                 => C3_ARB_TIME_SLOT_8,
   C_ARB_TIME_SLOT_9                 => C3_ARB_TIME_SLOT_9,
   C_ARB_TIME_SLOT_10                => C3_ARB_TIME_SLOT_10,
   C_ARB_TIME_SLOT_11                => C3_ARB_TIME_SLOT_11,
   C_MEM_TRAS                        => C3_MEM_TRAS,
   C_MEM_TRCD                        => C3_MEM_TRCD,
   C_MEM_TREFI                       => C3_MEM_TREFI,
   C_MEM_TRFC                        => C3_MEM_TRFC,
   C_MEM_TRP                         => C3_MEM_TRP,
   C_MEM_TWR                         => C3_MEM_TWR,
   C_MEM_TRTP                        => C3_MEM_TRTP,
   C_MEM_TWTR                        => C3_MEM_TWTR,
   C_MEM_ADDR_ORDER                  => C3_MEM_ADDR_ORDER,
   C_NUM_DQ_PINS                     => C3_NUM_DQ_PINS,
   C_MEM_TYPE                        => C3_MEM_TYPE,
   C_MEM_DENSITY                     => C3_MEM_DENSITY,
   C_MEM_BURST_LEN                   => C3_MEM_BURST_LEN,
   C_MEM_CAS_LATENCY                 => C3_MEM_CAS_LATENCY,
   C_MEM_ADDR_WIDTH                  => C3_MEM_ADDR_WIDTH,
   C_MEM_BANKADDR_WIDTH              => C3_MEM_BANKADDR_WIDTH,
   C_MEM_NUM_COL_BITS                => C3_MEM_NUM_COL_BITS,
   C_MEM_DDR1_2_ODS                  => C3_MEM_DDR1_2_ODS,
   C_MEM_DDR2_RTT                    => C3_MEM_DDR2_RTT,
   C_MEM_DDR2_DIFF_DQS_EN            => C3_MEM_DDR2_DIFF_DQS_EN,
   C_MEM_DDR2_3_PA_SR                => C3_MEM_DDR2_3_PA_SR,
   C_MEM_DDR2_3_HIGH_TEMP_SR         => C3_MEM_DDR2_3_HIGH_TEMP_SR,
   C_MEM_DDR3_CAS_LATENCY            => C3_MEM_DDR3_CAS_LATENCY,
   C_MEM_DDR3_ODS                    => C3_MEM_DDR3_ODS,
   C_MEM_DDR3_RTT                    => C3_MEM_DDR3_RTT,
   C_MEM_DDR3_CAS_WR_LATENCY         => C3_MEM_DDR3_CAS_WR_LATENCY,
   C_MEM_DDR3_AUTO_SR                => C3_MEM_DDR3_AUTO_SR,
   C_MEM_DDR3_DYN_WRT_ODT            => C3_MEM_DDR3_DYN_WRT_ODT,
   C_MEM_MOBILE_PA_SR                => C3_MEM_MOBILE_PA_SR,
   C_MEM_MDDR_ODS                    => C3_MEM_MDDR_ODS,
   C_MC_CALIB_BYPASS                 => C3_MC_CALIB_BYPASS,
   C_MC_CALIBRATION_MODE             => C3_MC_CALIBRATION_MODE,
   C_MC_CALIBRATION_DELAY            => C3_MC_CALIBRATION_DELAY,
   C_SKIP_IN_TERM_CAL                => C3_SKIP_IN_TERM_CAL,
   C_SKIP_DYNAMIC_CAL                => C3_SKIP_DYNAMIC_CAL,
   C_LDQSP_TAP_DELAY_VAL             => C3_LDQSP_TAP_DELAY_VAL,
   C_LDQSN_TAP_DELAY_VAL             => C3_LDQSN_TAP_DELAY_VAL,
   C_UDQSP_TAP_DELAY_VAL             => C3_UDQSP_TAP_DELAY_VAL,
   C_UDQSN_TAP_DELAY_VAL             => C3_UDQSN_TAP_DELAY_VAL,
   C_DQ0_TAP_DELAY_VAL               => C3_DQ0_TAP_DELAY_VAL,
   C_DQ1_TAP_DELAY_VAL               => C3_DQ1_TAP_DELAY_VAL,
   C_DQ2_TAP_DELAY_VAL               => C3_DQ2_TAP_DELAY_VAL,
   C_DQ3_TAP_DELAY_VAL               => C3_DQ3_TAP_DELAY_VAL,
   C_DQ4_TAP_DELAY_VAL               => C3_DQ4_TAP_DELAY_VAL,
   C_DQ5_TAP_DELAY_VAL               => C3_DQ5_TAP_DELAY_VAL,
   C_DQ6_TAP_DELAY_VAL               => C3_DQ6_TAP_DELAY_VAL,
   C_DQ7_TAP_DELAY_VAL               => C3_DQ7_TAP_DELAY_VAL,
   C_DQ8_TAP_DELAY_VAL               => C3_DQ8_TAP_DELAY_VAL,
   C_DQ9_TAP_DELAY_VAL               => C3_DQ9_TAP_DELAY_VAL,
   C_DQ10_TAP_DELAY_VAL              => C3_DQ10_TAP_DELAY_VAL,
   C_DQ11_TAP_DELAY_VAL              => C3_DQ11_TAP_DELAY_VAL,
   C_DQ12_TAP_DELAY_VAL              => C3_DQ12_TAP_DELAY_VAL,
   C_DQ13_TAP_DELAY_VAL              => C3_DQ13_TAP_DELAY_VAL,
   C_DQ14_TAP_DELAY_VAL              => C3_DQ14_TAP_DELAY_VAL,
   C_DQ15_TAP_DELAY_VAL              => C3_DQ15_TAP_DELAY_VAL
   )
port map
(
   mcb3_dram_dq                         => mcb3_dram_dq,
   mcb3_dram_a                          => mcb3_dram_a,
   mcb3_dram_ba                         => mcb3_dram_ba,
   mcb3_dram_ras_n                      => mcb3_dram_ras_n,
   mcb3_dram_cas_n                      => mcb3_dram_cas_n,
   mcb3_dram_we_n                       => mcb3_dram_we_n,
   mcb3_dram_odt                        => mcb3_dram_odt,
   mcb3_dram_cke                        => mcb3_dram_cke,
   mcb3_dram_dm                         => mcb3_dram_dm,
   mcb3_dram_udqs                       => mcb3_dram_udqs,
   mcb3_dram_udqs_n                     => mcb3_dram_udqs_n,
   mcb3_rzq                             => mcb3_rzq,
   mcb3_zio                             => mcb3_zio,
   mcb3_dram_udm                        => mcb3_dram_udm,
   calib_done                      => c3_calib_done,
   async_rst                       => c3_async_rst,
   sysclk_2x                       => c3_sysclk_2x,
   sysclk_2x_180                   => c3_sysclk_2x_180,
   pll_ce_0                        => c3_pll_ce_0,
   pll_ce_90                       => c3_pll_ce_90,
   pll_lock                        => c3_pll_lock,
   mcb_drp_clk                     => c3_mcb_drp_clk,
   mcb3_dram_dqs                        => mcb3_dram_dqs,
   mcb3_dram_dqs_n                      => mcb3_dram_dqs_n,
   mcb3_dram_ck                         => mcb3_dram_ck,
   mcb3_dram_ck_n                       => mcb3_dram_ck_n,
   p0_cmd_clk                           =>  c3_clk0, ----------------important-------------------
																	  ------------------ make sure valid clock is connected --------
   p0_cmd_en                            =>  c3_p0_cmd_en,
   p0_cmd_instr                         =>  c3_p0_cmd_instr,
   p0_cmd_bl                            =>  c3_p0_cmd_bl,
   p0_cmd_byte_addr                     =>  c3_p0_cmd_byte_addr,
   p0_cmd_empty                         =>  c3_p0_cmd_empty,
   p0_cmd_full                          =>  c3_p0_cmd_full,
   p0_wr_clk                            =>  c3_clk0, ----------------important-------------------
																		  ------------------ make sure valid clock is connected --------
   p0_wr_en                             =>  c3_p0_wr_en,
   p0_wr_mask                           =>  c3_p0_wr_mask,
   p0_wr_data                           =>  c3_p0_wr_data,
   p0_wr_full                           =>  c3_p0_wr_full,
   p0_wr_empty                          =>  c3_p0_wr_empty,
   p0_wr_count                          =>  c3_p0_wr_count,
   p0_wr_underrun                       =>  c3_p0_wr_underrun,
   p0_wr_error                          =>  c3_p0_wr_error,
   p0_rd_clk                            =>  c3_clk0, ----------------important-------------------
																		  ------------------ make sure valid clock is connected --------
   p0_rd_en                             =>  c3_p0_rd_en,
   p0_rd_data                           =>  c3_p0_rd_data,
   p0_rd_full                           =>  c3_p0_rd_full,
   p0_rd_empty                          =>  c3_p0_rd_empty,
   p0_rd_count                          =>  c3_p0_rd_count,
   p0_rd_overflow                       =>  c3_p0_rd_overflow,
   p0_rd_error                          =>  c3_p0_rd_error,
   selfrefresh_enter                    =>  c3_selfrefresh_enter,
   selfrefresh_mode                     =>  c3_selfrefresh_mode
);


fifo_sdram_wr : fifo_sdram_wr_w32_1024_r64_512 port map (
	rst => ep07wire(2),
	wr_clk => fifo_photon_wr_clk,
	rd_clk => c3_clk0,
	din => fifo_photon_din,
	wr_en => master_logic(17),
	rd_en => pipe_in_sdram_read,
	dout => pipe_in_sdram_data,
	full => open,
	empty => pipe_in_sdram_empty,
	valid => pipe_in_sdram_valid,
	rd_data_count => pipe_in_sdram_count,
	wr_data_count => open
);

fifo_sdram_rd : fifo_sdram_rd_w64_512_r16_2048 port map (
	rst => ep07wire(2),
	wr_clk => c3_clk0,
	rd_clk  => ti_clk,
	din  => pipe_out_sdram_data,
	wr_en  => pipe_out_sdram_write,
	rd_en  => time_resolved_pipe_out_read,
	dout => time_resolved_pipe_out_data,
	full => pipe_out_sdram_full,
	empty => open,
	valid => open,
	rd_data_count => open,
	wr_data_count => pipe_out_sdram_count
);



--------- DDS fifo --------------
fifo_dds: fifo_dds_w16_2048_r16_2048 port map(
		rst=>fifo_dds_rst,
		wr_clk=>ti_clk,
		rd_clk=>fifo_dds_rd_clk,
		din=> pipe_in_data_dds,
		wr_en=> pipe_in_write_dds,
		rd_en=> fifo_dds_rd_en, 
		dout=> fifo_dds_dout,
		full=> fifo_dds_full,
		empty=> fifo_dds_empty,
		wr_data_count=>fifo_dds_wr_data_count);
		
pipe_in_ready_dds <= '1'; ---- enable pipe in. The only pipe in used in this design is writing of the pulse into this fifo.
fifo_dds_rst <= ep40wire(7); -------- this fifo never gets reset because if there's anything in the fifo, it will get written into the ram right away
led(7) <= not fifo_dds_empty;
led(6 downto 4) <= not ep04wire(2 downto 0);
led(3 downto 2) <= ep00wire(7 downto 6);
led(1) <= not line_triggering_pulse;
led(0) <= not logic_in(0);
--led(0)<=not ram_full_flag;
---------------------------------------------------------
---------- condition read clk ---------------------------
---------------------------------------------------------

	process(clk_20, fifo_dds_rd_clk_temp)
	begin
		if (rising_edge(clk_20)) then
			if (fifo_dds_rd_clk_temp = '1') then
				fifo_dds_rd_clk <= '1';
			else
				fifo_dds_rd_clk <= '0';
			end if;
		end if;
	end process;

---============= DDS stuff ==============================
---------------------------------------------------------

dds_logic_data_out <= fifo_dds_dout;
fifo_dds_rd_clk_temp <= dds_logic_fifo_rd_clk;
fifo_dds_rd_en <= dds_logic_fifo_rd_en;
dds_logic_fifo_empty <= fifo_dds_empty;
dds_logic_ram_reset <= master_logic(19) or ep40wire(4); -----------dds reset----------
dds_logic_step_to_next_value <= master_logic(18) or ep40wire(5);
dds_logic_reset_dds_chip <= ep40wire(6);
dds_logic_address <= ep04wire(2 downto 0); ---------------set dds channel
dds_logic_ram_reset_manual<=ep40wire(8);

	
---------------------------------------------------------------------------------------
----------- general pll. This generated 200 MHz, 100 MHz and 20 MHz from 100 MHz ------
---------------------------------------------------------------------------------------

pll: clk_pll port map(

	-- Clock in ports
		CLK_IN1 => clk_in1,
   -- Clock out ports
		CLK_OUT1 => clk_200,
		CLK_OUT2 => clk_100,
		CLK_OUT3 => clk_20);
		
-----------------------------------------------------------------------------------------------------		
----------- this fifo is to store data from the pc before writing to the block ram for pulser -------
----------- this fifo is first-word-fall-through!!! -------------------------------------------------
-----------------------------------------------------------------------------------------------------

fifo_pulse_seq: fifo_pulse_seq_w16_1024_r64_256 port map(
		rst=>fifo_pulser_rst,
		wr_clk=>ti_clk,
		rd_clk=>fifo_pulser_rd_clk,
		din=> pipe_in_data,
		wr_en=> pipe_in_write,
		rd_en=> fifo_pulser_rd_en, 
		dout=> fifo_pulser_dout,
		full=> fifo_pulser_full,
		empty=> fifo_pulser_empty,
		rd_data_count=>fifo_pulser_rd_data_count);
		
pipe_in_ready <= '1'; ---- enable pipe in. The only pipe in used in this design is writing of the pulse into this fifo.
fifo_pulser_rst <= '0'; -------- this fifo never gets reseted because if there's anything in the fifo, it will get written into the ram right away

---------- RAM WRITER PROCESS-------------------
---------- write from fifo to block ram to store pulser ----------------
---------- this ram will store the pulse sequence ----------------------

ram: ram_pulser port map (
		clka => pulser_ram_clka,
		wea => pulser_ram_wea,
		addra => pulser_ram_addra,
		dina => pulser_ram_dina,
		clkb => pulser_ram_clkb,
		addrb => pulser_ram_addrb,
		doutb => pulser_ram_doutb);
		
	process (clk_100,pulser_ram_reset)
		variable write_ram_address: integer range 0 to 16383:=0;
		variable ram_process_count: integer range 0 to 8:=0;
	begin
		----- reset ram -----
		----- This doesn't really reset the ram but only put the address to zero so that the next writing 
		----- from the fifo to the ram will start from the first address. Since each pulse will end with all zeros anyway
		----- it's ok to have old information in the ram. The execution will never get past the end line.
		if (pulser_ram_reset = '1') then
			write_ram_address := 0;
			ram_process_count := 0;
		elsif rising_edge(clk_100) then
			case ram_process_count is
				--------- first two prepare and check whether there is anything in the fifo. This can be done by looking at the pin
				--------- fifo_pulser empty. 
				when 0 => fifo_pulser_rd_clk <='1';
							 fifo_pulser_rd_en <= '0';
							 pulser_ram_wea <="0";
							 ram_process_count := 1;
				when 1 => fifo_pulser_rd_clk <='0';
							 if (fifo_pulser_empty = '1') then ---- '1' is empty. Go back to case 0 
								ram_process_count:=0; 
							 else 
								ram_process_count := 2;  ---- if there's anything in the fifo, go to the next case
							 end if;
				-------- there's sth in the fifo ---------
				when 2 => fifo_pulser_rd_en <= '1';
							 ram_process_count:=3;
				when 3 => fifo_pulser_rd_clk <= '1'; ------------- read from fifo --------------
							 pulser_ram_wea <="1";
							 pulser_ram_clka <= '0';
							 ram_process_count:=4;
				when 4 => fifo_pulser_rd_clk <= '0';
							 ram_process_count:=5;
				
				---------- prepare data and address that are about to be written to the ram------
				
				when 5 => pulser_ram_addra <= CONV_STD_LOGIC_VECTOR(write_ram_address,14);
							 pulser_ram_dina <= fifo_pulser_dout;
							 ram_process_count:=6;
				when 6 => pulser_ram_clka <= '1'; ----------write to ram
							 ram_process_count:=7;
				when 7 => write_ram_address:=write_ram_address+1; ----- increase address by one
							 ram_process_count:=8;
				----- check again if the fifo is empty or not. Basically this whole process will
				----- keep writing to ram until fifo is empty.
				when 8 => if (fifo_pulser_empty = '1') then 
								ram_process_count:=0;
							 else 
								ram_process_count:=2; 
							 end if;
			end case;
		end if;
	end process;
	
	
------- generate slow clock at 1 MHz ------

	process (clk_20)
		variable count: integer range 0 to 21 :=0;
	begin
		if (rising_edge(clk_20)) then
			count := count + 1;
			if (count <= 10) then
				clk_1 <= '1';
			elsif (count <= 20) then
				clk_1 <= '0';
			elsif (count=21) then
				count :=0;
			end if;
		end if;
	end process;
	
	bnc_out <= "0000";
	
-----------------------------------------------------------------------------
-----------------------------------------------------------------------------
----- line triggering generation conditioning --------------

	process (clk_20, logic_in(0))	
		variable duration_count: integer range 0 to 15:=0;
		variable delay_count: integer range 0 to 15:=0;
	begin 
		if (logic_in(0) = '0') then
			duration_count := 0;
			delay_count := 0;
			line_triggering_conditioned <= '0';
		elsif (rising_edge(clk_20)) then
			if (delay_count < 7) then
				delay_count := delay_count + 1;
			elsif (delay_count >= 7) then
				if (duration_count < 7) then
					duration_count := duration_count + 1;
					line_triggering_conditioned <= '1';
				elsif (duration_count >= 7) then
					line_triggering_conditioned <= '0';
				end if;
			end if;
		end if;
	end process;
	
----- line triggering generation --------------	

	process (clk_1, line_triggering_conditioned)	
		variable duration_count: integer range 0 to 65535:=0;
		variable delay_count: integer range 0 to 65535:=0;
	begin 
		if (line_triggering_conditioned = '1') then
			duration_count := 0;
			delay_count := 0;
			line_triggering_pulse <= '0';
		elsif (rising_edge(clk_1)) then
			if (delay_count < CONV_INTEGER(UNSIGNED (ep06wire(15 downto 0)))) then
				delay_count := delay_count + 1;
			elsif (delay_count >= CONV_INTEGER(UNSIGNED (ep06wire(15 downto 0)))) then
				if (duration_count < 15) then
					duration_count := duration_count + 1;
					line_triggering_pulse <= '1';
				elsif (duration_count >= 15) then
					line_triggering_pulse <= '0';
				end if;
			end if;
		end if;
	end process;

------------------------------- pulser module -------------------------------
----- There is a main counter that go through each step in the RAM data. -----
----- The array of data of 64 bit has two portion. Time stamp and logic. -----
----- The convention is to specify which state of the logic at each time stamp
----- The first time stamp doesn't do anything. And the pulse will stop until
----- the end line is reached. The endline is specified from timestamp = 0. ---
----- The logic in the endline also doesn't do anything.----------------------


	process (clk_100, pulser_counter_reset)
		variable seq_count: INTEGER range 0 to 65535;--- count number of seq run
		variable count1: INTEGER range 0 to 3:=0;
		variable time_count: INTEGER:=0;
		variable time_stamp: INTEGER:=0;
		variable ram_read_address: integer range 0 to 16383:=0;
		variable ram_process_count: INTEGER range 0 to 10:=0;
		variable ram_data_out_1: STD_LOGIC_VECTOR (63 downto 0);
		variable ram_data_out_2: STD_LOGIC_VECTOR (63 downto 0);
	begin
		IF (pulser_counter_reset = '1') then
			ram_process_count:=0;
			ram_read_address:=0;
			count1:=0;
			time_count:=0;
			time_stamp:=0;
			master_logic <= "00000000000000000000000000000000";
			pulser_sequence_done <= '0';----------------"seq done flag" is deasserted
			seq_count:=0;
		ELSIF (rising_edge(clk_100)) THEN
			IF (pulser_start_bit = '1') THEN ------ This means the "run" flaged is set such that the pulse runs.
			CASE ram_process_count IS
			
				------------- read initial configuration --------------
				when 0 =>   ram_read_address:=0;
							   -----------wait for line triggering--------
								IF ((line_triggering_enabled = '1' and line_triggering_pulse = '1') or (line_triggering_enabled = '0')) then
									ram_process_count := ram_process_count + 1;
								END IF;
				WHEN 1 =>   pulser_ram_clkb <= '1';
								ram_process_count := ram_process_count + 1;				
				WHEN 2 =>   master_logic <= pulser_ram_doutb (31 downto 0);
							   ram_read_address:=1;
							   pulser_ram_clkb <= '0';
							   ram_process_count := ram_process_count + 1;
				WHEN 3 =>   pulser_ram_clkb <= '1';
								ram_process_count := ram_process_count + 1;
				WHEN 4 => 	ram_data_out_2:=pulser_ram_doutb;
								time_stamp := CONV_INTEGER(UNSIGNED (ram_data_out_2(61 downto 32)));
								ram_read_address := 2;
								ram_process_count := ram_process_count + 1;
								
				---- read process -----		 
				WHEN 5 => IF (time_count+1 = time_stamp) THEN ----------- approaching the time stamp
								IF (count1 = 0) THEN
									pulser_ram_clkb <= '0';
									count1 :=1;
								ELSIF (count1 = 1) THEN
									pulser_ram_clkb <= '1'; -----------ram data is read
									count1 :=2;
								ELSIF (count1 = 2) THEN
									pulser_ram_clkb <= '0';
									ram_data_out_1 := ram_data_out_2;
									ram_data_out_2 := pulser_ram_doutb; -----------latch output from ram to ram_data_out
									count1:=3;
								ELSIF (count1 = 3) THEN
									count1:=0;
									time_count := time_count+1;
									ram_read_address := ram_read_address+1;
									time_stamp := CONV_INTEGER(UNSIGNED (ram_data_out_2(61 downto 32)));
										IF (time_stamp = 0) THEN ----------- if the end line (specified by timestamp = 0) is reached.
											IF (pulser_infinite_loop = '1') then ---- if it's in the infinite looped mode then jump back to the beginning
												ram_process_count:=0;
												ram_read_address:=0;
												count1:=0;
												time_count:=0;
												time_stamp:=0;
												master_logic <= ram_data_out_1(31 downto 0);
												seq_count:=seq_count+1;-------- increase number of sequence count --------
												if (CONV_INTEGER(UNSIGNED (ep05wire(15 downto 0))) /= 0) then
													if (seq_count = CONV_INTEGER(UNSIGNED (ep05wire(15 downto 0)))) then
														master_logic <= "00000000000000000000000000000000";
														ram_process_count := 6;
													end if;
												end if;
											else
												-------------- one shot mode, after this go to limbo -------
												master_logic <= "00000000000000000000000000000000";
												ram_process_count := ram_process_count+1;
											end if;
										ELSE
											master_logic <= ram_data_out_1(31 downto 0);
										END IF;
								END IF;
							 ELSE
								----------- if the time stamp is not yet reached, keeps counting -------
								IF (count1 = 0) THEN
									count1 :=1;
								ELSIF (count1 = 1) THEN
									count1 :=2;
								ELSIF (count1 = 2) THEN
									count1:=3;
								ELSIF (count1 = 3) THEN
									count1:=0;
									time_count := time_count+1;
								END IF;
							 END IF;
				------- this is limbo, you can't escape from here. To get out you need to reset the pulser. -----
				WHEN 6 => pulser_sequence_done <= '1';
				WHEN OTHERS => NULL;
				
			END CASE;
			END IF;
			------ link the read address to the ram address in the process
			pulser_ram_addrb<=conv_std_logic_vector(ram_read_address,14);
			------ get timestamp data ready. This is to be used to tag photon in the time resolved photon process ----
			photon_time_tag(31 downto 2) <= CONV_STD_LOGIC_VECTOR(time_count,30);
			photon_time_tag(1 downto 0) <= CONV_STD_LOGIC_VECTOR(count1,2);
			------ The number of sequence looped------------------------
			seq_count_bit <= CONV_STD_LOGIC_VECTOR(seq_count,16);
		END IF;
		
	end process;
	
	---------------- testing process -----------------------------
	process (clk_200, pmt_sampled)
	begin
		IF rising_edge(clk_200) then
			IF (pmt_sampled = '1') then
				pmt_synced <= '1';
				fifo_photon_wr_clk <= '1';
			else
				pmt_synced <= '0';
				fifo_photon_din <= photon_time_tag;
				fifo_photon_wr_clk <= '0';
			end if;
		end if;
	end process;
	
	process (clk_200, pmt_input)
	begin
		IF rising_edge(clk_200) then
			pmt_sampled <= pmt_input;-- and clk_100;
		END if;
	end process;
	

-------------------------------------------------------------
---------------------- logic_out table ----------------------
-------------------------------------------------------------
----- 0 ------ 866DP
----- 1 ------ crystallization
----- 2 ------ bluePI
----- 3 ------ 110DP
----- 4 ------ axial
----- 5 ------ camera
----- 6 
----- 7 ------ pump
----- 8
----- 9
----- 16 ----- pmt counter trigger for differential mode (DiffCountTrigger)
----- 17 ----- time resolved photon counting enable (TimeResolvedCount)
----- 18 ----- dds step to next value
----- 19 ----- reset dds
----- 20 ----- readout_should_count
----- 21 ----- advance dds 729
----- 22 ----- reset dds 729
-----------------------------------------------------------------------------------
------ This part: if ep02 = '0' and ep 03 = '0', then follow the logic
------------------if ep02 = '0' and ep 03 = '1', then invert the logic
------------------if ep02 = '1' and ep 03 = '0', then always '0'
------------------if ep02 = '1' and ep 03 = '1', then always '1'


	LOGIC_OUT(0) <= master_logic(0) 		WHEN (ep02wire(0)='0' AND ep03wire(0)='0') ELSE
						 NOT master_logic(0)   WHEN (ep02wire(0)='0' AND ep03wire(0)='1') ELSE
						 '0' 					WHEN (ep02wire(0)='1' AND ep03wire(0)='0') ELSE
						 '1';
	LOGIC_OUT(1) <= master_logic(1) 		WHEN (ep02wire(1)='0' AND ep03wire(1)='0') ELSE
						 NOT master_logic(1)   WHEN (ep02wire(1)='0' AND ep03wire(1)='1') ELSE
						 '0' 					WHEN (ep02wire(1)='1' AND ep03wire(1)='0') ELSE
						 '1';
	LOGIC_OUT(2) <= master_logic(2) 		WHEN (ep02wire(2)='0' AND ep03wire(2)='0') ELSE
						 NOT master_logic(2)   WHEN (ep02wire(2)='0' AND ep03wire(2)='1') ELSE
						 '0' 					WHEN (ep02wire(2)='1' AND ep03wire(2)='0') ELSE
						 '1';
	LOGIC_OUT(3) <= master_logic(3) 		WHEN (ep02wire(3)='0' AND ep03wire(3)='0') ELSE
						 NOT master_logic(3)   WHEN (ep02wire(3)='0' AND ep03wire(3)='1') ELSE
						 '0' 					WHEN (ep02wire(3)='1' AND ep03wire(3)='0') ELSE
						 '1';
	LOGIC_OUT(4) <= master_logic(4) 		WHEN (ep02wire(4)='0' AND ep03wire(4)='0') ELSE
						 NOT master_logic(4)   WHEN (ep02wire(4)='0' AND ep03wire(4)='1') ELSE
						 '0' 					WHEN (ep02wire(4)='1' AND ep03wire(4)='0') ELSE
						 '1';
	LOGIC_OUT(5) <= master_logic(5) 		WHEN (ep02wire(5)='0' AND ep03wire(5)='0') ELSE
						 NOT master_logic(5)   WHEN (ep02wire(5)='0' AND ep03wire(5)='1') ELSE
						 '0' 					WHEN (ep02wire(5)='1' AND ep03wire(5)='0') ELSE
						 '1';
	LOGIC_OUT(6) <= master_logic(6) 		WHEN (ep02wire(6)='0' AND ep03wire(6)='0') ELSE
						 NOT master_logic(6)   WHEN (ep02wire(6)='0' AND ep03wire(6)='1') ELSE
						 '0' 					WHEN (ep02wire(6)='1' AND ep03wire(6)='0') ELSE
						 '1';
	LOGIC_OUT(7) <= master_logic(7) 		WHEN (ep02wire(7)='0' AND ep03wire(7)='0') ELSE
						 NOT master_logic(7)   WHEN (ep02wire(7)='0' AND ep03wire(7)='1') ELSE
						 '0' 					WHEN (ep02wire(7)='1' AND ep03wire(7)='0') ELSE
						 '1';
	LOGIC_OUT(8) <= master_logic(8) 		WHEN (ep02wire(8)='0' AND ep03wire(8)='0') ELSE
						 NOT master_logic(8)   WHEN (ep02wire(8)='0' AND ep03wire(8)='1') ELSE
						 '0' 					WHEN (ep02wire(8)='1' AND ep03wire(8)='0') ELSE
						 '1';
	LOGIC_OUT(9) <= master_logic(9) 		WHEN (ep02wire(9)='0' AND ep03wire(9)='0') ELSE
						 NOT master_logic(9)   WHEN (ep02wire(9)='0' AND ep03wire(9)='1') ELSE
						 '0' 					WHEN (ep02wire(9)='1' AND ep03wire(9)='0') ELSE
						 '1';
	LOGIC_OUT(10) <= master_logic(10) 		WHEN (ep02wire(10)='0' AND ep03wire(10)='0') ELSE
						 NOT master_logic(10)   WHEN (ep02wire(10)='0' AND ep03wire(10)='1') ELSE
						 '0' 					WHEN (ep02wire(10)='1' AND ep03wire(10)='0') ELSE
						 '1';
	LOGIC_OUT(11) <= master_logic(11) 		WHEN (ep02wire(11)='0' AND ep03wire(11)='0') ELSE
						 NOT master_logic(11)   WHEN (ep02wire(11)='0' AND ep03wire(11)='1') ELSE
						 '0' 					WHEN (ep02wire(11)='1' AND ep03wire(11)='0') ELSE
						 '1';									 

	LOGIC_OUT(15 downto 12) <= master_logic(15 downto 12);


----------- Get flag from epwire  ----------------
----------- ep00wire(0) is the normal pmt or differential pmt mode -------
pulser_counter_reset <= ep40wire(0);	
pulser_ram_reset <= ep40wire(1);	
pulser_infinite_loop <= ep00wire(1);			
pulser_start_bit <= ep00wire(2);	
line_triggering_enabled <= ep00wire(3);

pulser_flag_register(0) <= pulser_sequence_done;




---------- this is to configure what to display on ep21wire ----
----------------------------------------------------------------

process (ti_clk)
begin
	if rising_edge(ti_clk) then
		if (ep00wire(7 downto 5) = "000") Then
			ep21wire <= pulser_flag_register;
		elsif (ep00wire(7 downto 5) = "001") then
			ep21wire <= seq_count_bit;
		elsif (ep00wire(7 downto 5) = "010") then
			ep21wire(10 downto 0) <= normal_pmt_rd_data_count;
		elsif (ep00wire(7 downto 5) = "100") then
			ep21wire(10 downto 0) <= readout_count_rd_data_count;
		else
			ep21wire <= "0000000000000000";
		end if;
	end if;
end process;
				

fifo_photon_wr_en <= master_logic(17);


normal_pmt_pipe_out_valid <= '1';
time_resolved_pipe_out_valid <= '1';

fifo_photon_rst <= ep40wire(3);	

i2c_sda    <= 'Z';
i2c_scl    <= 'Z';
hi_muxsel  <= '0';

------------------------------------------------------------
---------------------------- NORMAL PMT --------------------
------------------------------------------------------------
--------- mode selection ------------
--------- This is to select whether it's a normal mode or differential mode ---------	

normal_pmt_count_trigger <= normal_pmt_auto_count_clk WHEN ep00wire(0) = '0' ELSE master_logic(16);
normal_pmt_count_period <= CONV_INTEGER(UNSIGNED (ep01wire (15 DOWNTO 0)));
	
--------- generate auto clock where the user set the period --------
	
process (clk_100,normal_pmt_fifo_reset)
	variable count: integer range 0 to 2147483647:=0;
begin
		IF (normal_pmt_fifo_reset = '1') THEN
			count:=0;
		ELSIF (rising_edge(clk_100)) THEN
			count:=count+1;
			IF (count = 1) THEN
				normal_pmt_auto_count_clk <= '0';
			ELSIF (count = normal_pmt_count_period*50000) THEN
				normal_pmt_auto_count_clk <= '1';
			ELSIF (count > normal_pmt_count_period*100000) THEN
				count:=0;
			END IF;
		END IF;
	END PROCESS;
	
	--------- trigger to reset FIFO -----
	normal_pmt_fifo_reset<=ep40wire(2);
	normal_pmt_block_aval <= '0' WHEN normal_pmt_rd_data_count = "00000000000" ELSE '1';
	
	
	-- FIFO for normal PMT: write in is 32 bit, read out 16 bit --
	fifo_normal_pmt: fifo_pmt_w32_1024_r16_2048 port map (rst => normal_pmt_fifo_reset,
													wr_clk => clk_100,
													rd_clk =>ti_clk,
													din => normal_pmt_fifo_data,
													wr_en => normal_pmt_wr_en,
													rd_en =>normal_pmt_pipe_out_read, 
													dout => normal_pmt_pipe_out_data,
													full =>normal_pmt_full,
													empty =>normal_pmt_empty,
													rd_data_count=>normal_pmt_rd_data_count
													);
	
	------ generate timing sequece -------
	------ write to fifo at the beginning of the count trigger ----
	------ the dead time that we can't count is very low and can be ignored ------
	process (clk_100, normal_pmt_count_trigger)   ----count_trigger_active_high----
		variable count: integer range 0 to 6:=6;
		variable wr_en_var: STD_LOGIC:='0';
		variable fifo_data_var:STD_LOGIC_VECTOR(31 DOWNTO 0):="00000000000000000000000000000000";
		variable pmt_count_reset_var: STD_LOGIC:='0';
	begin
		if (normal_pmt_count_trigger = '0') then
			count:=0;
		elsif (rising_edge(clk_100)) then
			case count IS
				WHEN 0 =>
					--define data--
					wr_en_var := '0';
					fifo_data_var (30 DOWNTO 0) := CONV_STD_LOGIC_VECTOR(pmt_count,31);
					fifo_data_var (31) := '0' WHEN ep00wire(0) = '0' ELSE 
														  '0'	WHEN (master_logic(0) = '1' AND ep00wire(0) = '1') ELSE 
														  '1';
					pmt_count_reset_var:='0';
					count:=count+1;
				WHEN 1 =>
					--enable write
					wr_en_var:='1';
					count:=count+1;
				WHEN 2 =>
					--disable write
					wr_en_var:='0';
					count:=count+1;
				WHEN 3 => 
					--enable reset of pmt counting
					pmt_count_reset_var:='1';
					count := count+1;
				WHEN 4 => 
					count := count+1;
				WHEN 5 =>
					-- disable reset of pmt counting
					pmt_count_reset_var:='0';
					count := count+1;
				WHEN 6 =>
					NULL;
			end case;	 
			normal_pmt_wr_en<=wr_en_var;
			normal_pmt_fifo_data<=fifo_data_var;
			pmt_count_reset<=pmt_count_reset_var;
		end if;
	end process;

	-- count pmt by incresaing the value of pmt_count every time pmt_synced edge is detected
	process (pmt_count_reset, pmt_synced)
	begin
		if (pmt_count_reset = '1') then
			pmt_count<=0;
		elsif (rising_edge(pmt_synced)) then
			pmt_count<=pmt_count+1;
		end if;
	end process;

-- READOUT COUNTING:
readout_should_count <= master_logic(20);
readout_count_fifo_reset <= ep40wire(4); 
readout_count_pipe_out_valid <= '1';

------------------ readout_count FIFO
fifo_readout: fifo_pmt_w32_1024_r16_2048 port map (rst => readout_count_fifo_reset,
									wr_clk => clk_100,
									rd_clk => ti_clk,
									din => readout_count_fifo_data,
									wr_en => readout_count_wr_en,
									rd_en =>readout_count_pipe_out_read, 
									dout => readout_count_pipe_out_data,
									full =>readout_pmt_full,
									empty =>readout_pmt_empty,
									rd_data_count=>readout_count_rd_data_count
								);


	-- count readout counts by incresaing the value of pmt_readout_count every time pmt_synced edge is detected
	process (readout_should_count, pmt_synced)
	begin
		if (readout_should_count = '0') then
			pmt_readout_count<=0;
		elsif (rising_edge(pmt_synced)) then 
			pmt_readout_count <= pmt_readout_count + 1;
		end if;
	end process;
	
	-- when readout_should_count is low, the counting is done and the result is written to the FIFO
	process(clk_100, readout_should_count,pmt_readout_count)
		variable count: integer range 0 to 2:=2;
		variable wr_en_var: STD_LOGIC:='0';
		variable fifo_data_var:STD_LOGIC_VECTOR(31 DOWNTO 0):="00000000000000000000000000000000"; 
		variable pmt_readout_count_var: INTEGER RANGE 0 TO 2147483647:=0; 
	begin
		if (readout_should_count = '1') then
			pmt_readout_count_var := pmt_readout_count;
			wr_en_var := '0';
			count := 0;
		elsif (rising_edge(clk_100)) then
			case count IS
				WHEN 0 =>
					--define data--
					wr_en_var := '0';
					fifo_data_var (31 DOWNTO 0) := CONV_STD_LOGIC_VECTOR(pmt_readout_count_var,32);
					pmt_readout_count_var := 0; --avoids a latch of not always defining pmt_readout_count_var--
					count:=count+1;
				WHEN 1 =>
					--enable write--
					wr_en_var := '1';
					count:=count+1;
				WHEN 2 =>
					--disable write--
					wr_en_var := '0';
			end case;	 
			readout_count_wr_en<=wr_en_var;
			readout_count_fifo_data<=fifo_data_var;
		end if;
	end process;
-- END READOUT COUNTING.

-- Instantiate the okHost and connect endpoints.
okHI : okHost port map (hi_in=>hi_in, hi_out=>hi_out, hi_inout=>hi_inout, hi_aa=>hi_aa, ti_clk=>ti_clk, ok1=>ok1, ok2=>ok2);
okWO : okWireOR    generic map (N=>8) port map (ok2=>ok2, ok2s=>ok2s);
wi00 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"00", ep_dataout=>ep00wire);
wi01 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"01", ep_dataout=>ep01wire);
wi02 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"02", ep_dataout=>ep02wire);
wi03 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"03", ep_dataout=>ep03wire);
wi04 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"04", ep_dataout=>ep04wire);
wi05 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"05", ep_dataout=>ep05wire);
wi06 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"06", ep_dataout=>ep06wire);
wi07 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"07", ep_dataout=>ep07wire);
ep40 : okTriggerIn  port map (ok1=>ok1,                                  ep_addr=>x"40", ep_clk=>clk_1, ep_trigger=>ep40wire);
wo21 : okWireOut   port map (ok1=>ok1, ok2=>ok2s( 1*17-1 downto 0*17 ), ep_addr=>x"21", ep_datain=>ep21wire);
wo22 : okWireOut   port map (ok1=>ok1, ok2=>ok2s( 4*17-1 downto 3*17 ), ep_addr=>x"22", ep_datain=>ep22wire);
wo23 : okWireOut   port map (ok1=>ok1, ok2=>ok2s( 8*17-1 downto 7*17 ), ep_addr=>x"23", ep_datain=>ep23wire);
ep80 : okBTPipeIn  port map (ok1=>ok1, ok2=>ok2s( 2*17-1 downto 1*17 ), ep_addr=>x"80", 
                             ep_write=>pipe_in_write, ep_blockstrobe=>bs_in, ep_dataout=>pipe_in_data, ep_ready=>pipe_in_ready);
ep81 : okBTPipeIn  port map (ok1=>ok1, ok2=>ok2s( 6*17-1 downto 5*17 ), ep_addr=>x"81", 
                             ep_write=>pipe_in_write_dds, ep_blockstrobe=>bs_in_dds, ep_dataout=>pipe_in_data_dds, ep_ready=>pipe_in_ready_dds);
----- read timetag from sdram -----
epA0 : okPipeOut port map (ok1=>ok1, ok2=>ok2s( 3*17-1 downto 2*17 ), ep_addr=>x"A0", 
                             ep_read=>time_resolved_pipe_out_read, ep_datain=>time_resolved_pipe_out_data);
----normal pmt ----
epA1 : okBTPipeOut port map (ok1=>ok1, ok2=>ok2s( 5*17-1 downto 4*17 ), ep_addr=>x"A1", 
                             ep_read=>normal_pmt_pipe_out_read, ep_blockstrobe=>bs_out, ep_datain=>normal_pmt_pipe_out_data, ep_ready=>normal_pmt_pipe_out_valid);
----readout pmt ----
epA2 : okBTPipeOut port map (ok1=>ok1, ok2=>ok2s( 7*17-1 downto 6*17 ), ep_addr=>x"A2", 
                             ep_read=>readout_count_pipe_out_read, ep_blockstrobe=>bs_out, ep_datain=>readout_count_pipe_out_data, ep_ready=>readout_count_pipe_out_valid);


end arch;