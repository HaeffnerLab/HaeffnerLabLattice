------------------------------------------------------------------------
-- FrontPanel Library Module Declarations (VHDL)
-- XEM6010
--
-- IDELAY and IODELAY fixed delays were determined empirically to meet
-- timing for particular devices on particular products.
--
-- Copyright (c) 2004-2011 Opal Kelly Incorporated
-- $Rev: 907 $ $Date: 2011-04-28 14:47:52 -0700 (Thu, 28 Apr 2011) $
------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.vcomponents.all;
entity okHost is
	port (
		hi_in    : in std_logic_vector(7 downto 0);
		hi_out   : out std_logic_vector(1 downto 0);
		hi_inout : inout std_logic_vector(15 downto 0);
		hi_aa    : inout std_logic;
		ti_clk   : out std_logic;
		ok1      : out std_logic_vector(30 downto 0);
		ok2      : in std_logic_vector(16 downto 0)
	);
end okHost;

architecture archHost of okHost is
	attribute box_type: string;
	
	component okCoreHarness port (
		okHC   : in    std_logic_vector(24 downto 0);
		okCH   : out   std_logic_vector(20 downto 0);
		ok1    : out   std_logic_vector(30 downto 0);
		ok2    : in    std_logic_vector(16 downto 0));
	end component;
	
	attribute box_type of okCoreHarness : component is "black_box";
	
	signal okHC            : std_logic_vector(24 downto 0);
	signal okCH            : std_logic_vector(20 downto 0);
	signal hi_datain       : std_logic_vector(15 downto 0);
	signal hi_datain_delay : std_logic_vector(15 downto 0);
	signal hi_dataout      : std_logic_vector(15 downto 0);
	signal hi_dataout_reg  : std_logic_vector(15 downto 0);
	signal hi_drive        : std_logic;
	signal ti_clk_int      : std_logic;
	signal dcm_clk0        : std_logic;
	signal rst1            : std_logic;
	signal rst2            : std_logic;
	signal rst3            : std_logic;
	signal rst4            : std_logic;
	signal rstin           : std_logic;
begin
	okHC(0)            <= ti_clk_int;
	okHC(7 downto 1)   <= hi_in(7 downto 1);
	okHC(23 downto 8)  <= hi_datain;
	ti_clk             <= ti_clk_int;
	
	-- Clock buffer for the Host Interface clock.
	hi_dcm : DCM_SP  port map (CLKIN     => hi_in(0),
	                           CLKFB     => ti_clk_int,
	                           CLK0      => dcm_clk0,
	                           PSCLK     => '0',
	                           PSEN      => '0',
	                           PSINCDEC  => '0',
	                           RST       => rstin,
	                           DSSEN     => '0');
	hi_clkbuf : BUFG port map (I=>dcm_clk0, O=>ti_clk_int);
	flop1 : FDS port map (D=>'0',  C=>hi_in(0), Q=>rst1, S=>'0');
	flop2 : FD  port map (D=>rst1, C=>hi_in(0), Q=>rst2);
	flop3 : FD  port map (D=>rst2, C=>hi_in(0), Q=>rst3);
	flop4 : FD  port map (D=>rst3, C=>hi_in(0), Q=>rst4);
	rstin <= (rst2 or rst3 or rst4);

	-- Bidirectional IOBUFs for the hi_data lines.
	hi_inout <= hi_dataout_reg when (hi_drive='0') else (others=>'Z');
	g1: for i in 0 to 15 generate
		idcomp: IODELAY2 generic map (
				IDELAY_TYPE=>"FIXED",
				IDELAY_VALUE=>50,
				DELAY_SRC=>"IDATAIN"
			) port map (
				IDATAIN => hi_inout(i),
				DATAOUT => hi_datain_delay(i),
				T       => '1',
				CAL     => '0',
				CE      => '0',
				CLK     => '0',
				INC     => '0',
				IOCLK0  => '0',
				IOCLK1  => '0',
				ODATAIN => '0',
				RST     => '0'
			);
	end generate g1;
	process (ti_clk_int) begin
		if rising_edge(ti_clk_int) then
			hi_drive       <= not okCH(2);         -- Must invert to place DFF in OLOGIC
			hi_dataout_reg <= okCH(18 downto 3);   -- OLOGIC
			hi_datain      <= hi_datain_delay;     -- ILOGIC
		end if;
	end process;

	obuf0 : OBUF  port map (I=>okCH(0), O=>hi_out(0));
	obuf1 : OBUF  port map (I=>okCH(1), O=>hi_out(1));
	tbuf  : IOBUF port map (I=>okCH(19), O=>okHC(24), T=>okCH(20), IO=>hi_aa);

	core0 : okCoreHarness port map(okHC=>okHC, okCH=>okCH, ok1=>ok1, ok2=>ok2);
end archHost;


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
entity okWireOR is
	generic (
		N     : integer := 1
	);
	port (
		ok2   : out std_logic_vector(16 downto 0);
		ok2s  : in  std_logic_vector(N*17-1 downto 0)
	);
end okWireOR;
architecture archWireOR of okWireOR is
begin
	process (ok2s)
		variable ok2_int : STD_LOGIC_VECTOR(16 downto 0);
	begin
		ok2_int := b"0_0000_0000_0000_0000";
		for i in N-1 downto 0 loop
			ok2_int := ok2_int or ok2s( (i*17+16) downto (i*17) );
		end loop;
		ok2 <= ok2_int;
	end process;
end archWireOR;


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
package FRONTPANEL is

	attribute box_type: string;
	
	component okHost port (
		hi_in    : in std_logic_vector(7 downto 0);
		hi_out   : out std_logic_vector(1 downto 0);
		hi_inout : inout std_logic_vector(15 downto 0);
		hi_aa    : inout std_logic;
		ti_clk   : out std_logic;
		ok1      : out std_logic_vector(30 downto 0);
		ok2      : in std_logic_vector(16 downto 0));
	end component;

	component okCoreHarness port (
		okHC   : in    std_logic_vector(24 downto 0);
		okCH   : out   std_logic_vector(20 downto 0);
		ok1    : out   std_logic_vector(30 downto 0);
		ok2    : in    std_logic_vector(16 downto 0));
	end component;
	attribute box_type of okCoreHarness : component is "black_box";

	component okWireIn port (
		ok1        : in std_logic_vector(30 downto 0);
		ep_addr    : in std_logic_vector(7 downto 0);
		ep_dataout : out std_logic_vector(15 downto 0));
	end component;
	attribute box_type of okWireIn : component is "black_box";

	component okWireOut port (
		ok1       : in std_logic_vector(30 downto 0);
		ok2       : out std_logic_vector(16 downto 0);
		ep_addr   : in std_logic_vector(7 downto 0);
		ep_datain : in std_logic_vector(15 downto 0));
	end component;
	attribute box_type of okWireOut : component is "black_box";

	component okTriggerIn port (
		ok1        : in std_logic_vector(30 downto 0);
		ep_addr    : in std_logic_vector(7 downto 0);
		ep_clk     : in std_logic;
		ep_trigger : out std_logic_vector(15 downto 0));
	end component;
	attribute box_type of okTriggerIn : component is "black_box";

	component okTriggerOut port (
		ok1        : in std_logic_vector(30 downto 0);
		ok2        : out std_logic_vector(16 downto 0);
		ep_addr    : in std_logic_vector(7 downto 0);
		ep_clk     : in std_logic;
		ep_trigger : in std_logic_vector(15 downto 0));
	end component;
	attribute box_type of okTriggerOut : component is "black_box";

	component okPipeIn port (
		ok1        : in std_logic_vector(30 downto 0);
		ok2        : out std_logic_vector(16 downto 0);
		ep_addr    : in std_logic_vector(7 downto 0);
		ep_write   : out std_logic;
		ep_dataout : out std_logic_vector(15 downto 0));
	end component;
	attribute box_type of okPipeIn : component is "black_box";

	component okPipeOut port (
		ok1        : in std_logic_vector(30 downto 0);
		ok2        : out std_logic_vector(16 downto 0);
		ep_addr    : in std_logic_vector(7 downto 0);
		ep_read    : out std_logic;
		ep_datain  : in std_logic_vector(15 downto 0));
	end component;
	attribute box_type of okPipeOut : component is "black_box";

	component okBTPipeIn port (
		ok1            : in std_logic_vector(30 downto 0);
		ok2            : out std_logic_vector(16 downto 0);
		ep_addr        : in std_logic_vector(7 downto 0);
		ep_write       : out std_logic;
		ep_blockstrobe : out std_logic;
		ep_dataout     : out std_logic_vector(15 downto 0);
		ep_ready       : in std_logic);
	end component;
	attribute box_type of okBTPipeIn : component is "black_box";

	component okBTPipeOut port (
		ok1            : in std_logic_vector(30 downto 0);
		ok2            : out std_logic_vector(16 downto 0);
		ep_addr        : in std_logic_vector(7 downto 0);
		ep_read        : out std_logic;
		ep_blockstrobe : out std_logic;
		ep_datain      : in std_logic_vector(15 downto 0);
		ep_ready       : in std_logic);
	end component;
	attribute box_type of okBTPipeOut : component is "black_box";

	component okWireOR
	generic (N : integer := 1);
	port (
		ok2   : out std_logic_vector(16 downto 0);
		ok2s  : in  std_logic_vector(N*17-1 downto 0));
	end component;

end FRONTPANEL;