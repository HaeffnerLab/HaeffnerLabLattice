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
		------- Logic In/Out ------
		--logic_out: out STD_LOGIC_VECTOR (31 downto 0);
		logic_in:  in STD_LOGIC_VECTOR (5 downto 0);
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

  -- Endpoint connections:
	------ which experiment control this ------
	signal ep00wire        : STD_LOGIC_VECTOR(15 downto 0):="0000000000000000";

	------ DDS channel ---------------------
	signal ep04wire		  : STD_LOGIC_VECTOR(15 downto 0);

	------ Trigger in ------
	signal ep40wire        : STD_LOGIC_VECTOR(15 downto 0);

	signal bs_in_dds, bs_out_dds   : STD_LOGIC;
	
	signal pipe_in_write_dds   : STD_LOGIC;
	signal pipe_in_ready_dds   : STD_LOGIC;
	signal pipe_in_data_dds    : STD_LOGIC_VECTOR(15 downto 0);
	
	--- CLOCKs -----

	--- clk 100 MHz from PLL.
	signal clk_100         : STD_LOGIC;
	--- clk 200 MHz from PLL to sample the input PMT signal. Any slower clock will miss the pulse ---
	signal clk_200         : STD_LOGIC;
	--- clk 20 MHz from PLL. Not used for anything right now ----
	signal clk_20          : STD_LOGIC; 
	
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

begin


-----------------------------------------------------------------------------

--------- DDS fifo --------------
fifo4: dds_fifo port map(
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
led(3 downto 1) <= ep00wire(7 downto 5);
led(0) <= '0';

---------------------------------------------------------
---------- conditioning read clk from DDS ---------------------------
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
dds_logic_ram_reset <= (logic_in(1) or ep40wire(4)) WHEN ep00wire(1 downto 0) = "00" else ---lattice
							 (logic_in(3) or ep40wire(4))  WHEN ep00wire(1 downto 0) = "01" else ---cct
							 (logic_in(5) or ep40wire(4))  WHEN ep00wire(1 downto 0) = "10" else ---squip
							  '0';-----------dds reset----------
dds_logic_step_to_next_value <= (logic_in(0) or ep40wire(5)) WHEN ep00wire(1 downto 0) = "00" else
							 (logic_in(2) or ep40wire(5))  WHEN ep00wire(1 downto 0) = "01" else
							 (logic_in(4) or ep40wire(5))  WHEN ep00wire(1 downto 0) = "10" else
							  '0';-----------dds reset----------
dds_logic_reset_dds_chip <= ep40wire(6);

dds_logic_address <= ep04wire(2 downto 0); ---------------set dds channel

----------------------------------------------------------------------
----------- general pll. This generated 200 MHz and 20 MHz from 100 MHz ------
pll: clk_pll_100_in_200_out port map(

	-- Clock in ports
		CLK_IN1 => clk1,
   -- Clock out ports
		CLK_OUT1 => clk_200,
		CLK_OUT2 => clk_100,
		CLK_OUT3 => clk_20);

i2c_sda    <= 'Z';
i2c_scl    <= 'Z';
hi_muxsel  <= '0';


-- Instantiate the okHost and connect endpoints.
okHI : okHost port map (hi_in=>hi_in, hi_out=>hi_out, hi_inout=>hi_inout, hi_aa=>hi_aa, ti_clk=>ti_clk, ok1=>ok1, ok2=>ok2);
okWO : okWireOR    generic map (N=>1) port map (ok2=>ok2, ok2s=>ok2s);
wi00 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"00", ep_dataout=>ep00wire);
wi04 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"04", ep_dataout=>ep04wire);
ep40 : okTriggerIn  port map (ok1=>ok1,                                  ep_addr=>x"40", ep_clk=>clk_20, ep_trigger=>ep40wire);
ep81 : okBTPipeIn  port map (ok1=>ok1, ok2=>ok2s( 1*17-1 downto 0*17 ), ep_addr=>x"81", 
                             ep_write=>pipe_in_write_dds, ep_blockstrobe=>bs_in_dds, ep_dataout=>pipe_in_data_dds, ep_ready=>pipe_in_ready_dds);
end arch;