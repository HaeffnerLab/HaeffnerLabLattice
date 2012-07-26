library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.std_logic_arith.all;
use IEEE.std_logic_misc.all;
use IEEE.std_logic_unsigned.all;
use work.FRONTPANEL.all;
library UNISIM;
use UNISIM.VComponents.all;

entity photon is
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
		clk1      : in    STD_LOGIC;
		------- BNC out -----
		bnc_in : in STD_LOGIC_VECTOR (7 downto 0);
		------- LED ------------------------
		led       : out   STD_LOGIC_VECTOR(7 downto 0);
		------- TO DDS ---------------------
		dds_logic_data_out : out STD_LOGIC_VECTOR (15 downto 0);
		dds_logic_fifo_rd_clk: in STD_LOGIC;
		dds_logic_fifo_rd_en: in STD_LOGIC;
		dds_logic_fifo_empty: out STD_LOGIC;
		dds_logic_ram_reset: out STD_LOGIC;
		dds_logic_step_to_next_value: out STD_LOGIC;
		dds_logic_reset_dds_chip: out STD_LOGIC;
		dds_logic_address : out STD_LOGIC_VECTOR (2 downto 0)
		
		--dds_logic : inout   STD_LOGIC_VECTOR(31 downto 0)
	);
end photon;

architecture arch of photon is
	---- clocking pll component -----
	component clk_pll_100_in_200_out port (
	-- Clock in ports
		CLK_IN1           : in     std_logic;
   -- Clock out ports
		CLK_OUT1          : out    std_logic;
		CLK_OUT2          : out    std_logic;
		CLK_OUT3          : out    std_logic);
	end component;
	
	---- fifo for dds ----
	
	component dds_fifo PORT (
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
	

	-- Target interface bus:
	signal ti_clk    : STD_LOGIC;
	signal ok1       : STD_LOGIC_VECTOR(30 downto 0);
	signal ok2       : STD_LOGIC_VECTOR(16 downto 0);
	signal ok2s      : STD_LOGIC_VECTOR(17*1-1 downto 0);

	------ Trigger in ------
	signal ep40wire        : STD_LOGIC_VECTOR(15 downto 0);

	----- These are for pipe logic ----
	
	signal pipe_in_write_dds   : STD_LOGIC;
	signal pipe_in_ready_dds   : STD_LOGIC;
	signal pipe_in_data_dds    : STD_LOGIC_VECTOR(15 downto 0);

	
	signal bs_in, bs_out   : STD_LOGIC;
	signal bs_in_dds, bs_out_dds   : STD_LOGIC;
	
		---- dds pulser signal ----
	
	signal   fifo_dds_rst 		: STD_LOGIC;
	signal	fifo_dds_rd_clk	: STD_LOGIC;
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
	
begin


-----------------------------------------------------------------------------

--------- DDS fifo --------------
fifo1: dds_fifo port map(
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
led(6 downto 0) <= "1111111";

---============= DDS stuff ==============================
---------------------------------------------------------
---- bnc(0) reset lattice
---- bnc(1) advance lattice
---- bnc(2) reset cct
---- bnc(3) advance cct
---- bnc(4) reset squip
---- bnc(5) advance squip

dds_logic_data_out <= fifo_dds_dout;
fifo_dds_rd_clk <= dds_logic_fifo_rd_clk;
fifo_dds_rd_en <= dds_logic_fifo_rd_en;
dds_logic_fifo_empty <= fifo_dds_empty;
dds_logic_ram_reset <= bnc_in(0);
dds_logic_step_to_next_value <= bnc_in(1);
dds_logic_reset_dds_chip <= ep40wire(6);

dds_logic_address <= "000"; ---------------set dds channel
	
i2c_sda    <= 'Z';
i2c_scl    <= 'Z';
hi_muxsel  <= '0';


-- Instantiate the okHost and connect endpoints.
okHI : okHost port map (hi_in=>hi_in, hi_out=>hi_out, hi_inout=>hi_inout, hi_aa=>hi_aa, ti_clk=>ti_clk, ok1=>ok1, ok2=>ok2);
okWO : okWireOR    generic map (N=>1) port map (ok2=>ok2, ok2s=>ok2s);
ep40 : okTriggerIn  port map (ok1=>ok1,                                  ep_addr=>x"40", ep_clk=>ti_clk, ep_trigger=>ep40wire);
ep81 : okBTPipeIn  port map (ok1=>ok1, ok2=>ok2s( 1*17-1 downto 0*17 ), ep_addr=>x"81", 
                             ep_write=>pipe_in_write_dds, ep_blockstrobe=>bs_in_dds, ep_dataout=>pipe_in_data_dds, ep_ready=>pipe_in_ready_dds);

end arch;