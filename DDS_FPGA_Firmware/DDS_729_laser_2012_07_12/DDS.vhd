
library ieee;
use ieee.std_logic_1164.all;
USE ieee.std_logic_arith.all;
use ieee.numeric_std.all;
USE work.all;

entity dds is
  port(
    clk_25 : in std_logic;
	 clk_in0: in std_logic;
	 
	 clk_out :out std_logic;

    -- LED driver ---
	 LED_CLK: OUT STD_LOGIC;
	 LED_SDI: OUT STD_LOGIC_VECTOR (0 DOWNTO 0);
	 LED_LE: OUT STD_LOGIC;
	 LED_OE: OUT STD_LOGIC;
	 
	 ----dip switch----
	 dip_in: in std_logic_vector (4 downto 0);
	 
    -- DDS control pins
    sdio_pin      : out std_logic;
    sdo_pin       : in    std_logic;
    sclk_pin      : out std_logic;
    ioreset_pin   : out std_logic;
    dds_reset_pin : out std_logic;

    ioup_pin : out std_logic;

    drover_pin : out std_logic;
    drctl_pin  : out std_logic;
    drhold_pin : out std_logic;

    osk_pin     : out std_logic;
    pargain_pin : out std_logic_vector(1 downto 0);---------parallel controlling pin
    profile_pin : out std_logic_vector(2 downto 0);
    txen_pin    : out std_logic;
    cs_pin      : out std_logic;
	 
	 pd_clk_pin : in std_logic; ----parallel port clk from dds

    -- DAC control pins
    parallel_data : out std_logic_vector(15 downto 0);
	 
    dac_wr_pin    : out std_logic;

    -- LVDS BUS input
	 bus_in_data : in std_logic_vector (15 downto 0);
	 bus_in_fifo_rd_clk : out std_logic;
	 bus_in_fifo_rd_en: out std_logic;
	 bus_in_fifo_empty: in std_logic;
	 bus_in_ram_reset: in std_logic;
	 bus_in_step_to_next_value: in std_logic;
	 bus_in_reset_dds_chip: in std_logic;
	 bus_in_address: in std_logic_vector (2 downto 0)
    );

end dds;

architecture behaviour of dds is

	SIGNAL LED_VALUE: STD_LOGIC_VECTOR (7 DOWNTO 0);
	
	CONSTANT CFR1_OP: STD_LOGIC_VECTOR (7 downto 0) := "00000000";
	CONSTANT CFR2_OP: STD_LOGIC_VECTOR (7 downto 0) := "00000001";
	CONSTANT CFR3_OP: STD_LOGIC_VECTOR (7 downto 0) := "00000010";
	CONSTANT FTW_OP: STD_LOGIC_VECTOR (7 downto 0) := "00000111";
	CONSTANT SINGLE_TONE0_OP: STD_LOGIC_VECTOR (7 downto 0) := "00001110";
	CONSTANT SINGLE_TONE1_OP: STD_LOGIC_VECTOR (7 downto 0) := "00001111";
	
	SIGNAL CFR1_DATA: STD_LOGIC_VECTOR (31 downto 0);
	SIGNAL CFR2_DATA: STD_LOGIC_VECTOR (31 downto 0);
	SIGNAL CFR3_DATA: STD_LOGIC_VECTOR (31 downto 0);
	SIGNAL FTW_DATA: STD_LOGIC_VECTOR (31 downto 0);
	SIGNAL SINGLE_TONE0_DATA: STD_LOGIC_VECTOR (63 downto 0);
	SIGNAL SINGLE_TONE1_DATA: STD_LOGIC_VECTOR (63 downto 0);
	
	SIGNAL DAC_OUT: STD_LOGIC_vector (13 downto 0) := "11111111111111";--"11011111111111"; ----this is -7.5 dBm output	
	SIGNAL parallel_data_signal: STD_LOGIC_VECTOR (15 downto 0);
	
	SIGNAL reset_fpga: STD_LOGIC;
	
	SIGNAL clk_100: STD_LOGIC;
	SIGNAL clk_system: STD_LOGIC;
	
	----------------------------------------------------------
	-----------RAM stuff--------------------------------------
	signal	dds_ram_data_in		: STD_LOGIC_VECTOR (15 DOWNTO 0);
	signal	dds_ram_rdaddress		: STD_LOGIC_VECTOR (9 DOWNTO 0);
	signal	dds_ram_rdclock		: STD_LOGIC;
	signal	dds_ram_wraddress		: STD_LOGIC_VECTOR (10 DOWNTO 0);
	signal	dds_ram_wrclock		: STD_LOGIC := '1';
	signal	dds_ram_wren		   : STD_LOGIC;
	signal	dds_ram_data_out		: STD_LOGIC_VECTOR (31 DOWNTO 0);
	signal 	dds_ram_reset        : STD_LOGIC;
	
	signal   fifo_dds_dout			: STD_LOGIC_VECTOR (15 downto 0);
	signal 	fifo_dds_empty			: STD_LOGIC;
	signal	fifo_dds_rd_clk      : STD_LOGIC;
	signal	fifo_dds_rd_en			: STD_LOGIC;
	
	signal   dds_step_to_next_freq : STD_LOGIC;
	
begin
	LED_CLK <= clk_system;
	--PLL: dds_pll PORT MAP (clk_in0,clk_system,clk_system_10); ---clk_in0 is 100 MHz, clk_system is 20 MHz. clk_system_10 is 10 MHz
	PLL: dds_pll PORT MAP (clk_25,clk_100); ---clk_in0 is 100 MHz, clk_system is 20 MHz. clk_system_10 is 10 MHz
	----------- RAM megafunction ---------
	ram1: dds_ram PORT MAP (dds_ram_data_in, dds_ram_rdaddress, dds_ram_rdclock, dds_ram_wraddress, dds_ram_wrclock, dds_ram_wren,dds_ram_data_out);
	
	------- generate slower clock --------
	process (clk_25)
		variable count: integer range 0 to 21 :=0;
	begin
		if (rising_edge(clk_25)) then
			count := count + 1;
			if (count <= 10) then
				clk_system <= '1';
			elsif (count <= 20) then
				clk_system <= '0';
			elsif (count=21) then
				count :=0;
			end if;
		end if;
	end process;
	----------- transfer data from pulser to DDS -----------
	--------------------------------------------------------
	fifo_dds_dout <= bus_in_data;
	
	fifo_dds_empty <= bus_in_fifo_empty;
	
	bus_in_fifo_rd_clk<=fifo_dds_rd_clk WHEN bus_in_address = dip_in(2 downto 0) else 'Z';
	bus_in_fifo_rd_en<=fifo_dds_rd_en WHEN bus_in_address = dip_in(2 downto 0) else 'Z';
	
	dds_ram_reset <= bus_in_ram_reset;
	dds_step_to_next_freq <= bus_in_step_to_next_value;
	dds_ram_rdclock<=clk_system;

	led_VALUE (3 downto 0) <= dds_ram_rdaddress(3 downto 0);
	led_VALUE (7 downto 5) <= bus_in_address;
	led_VALUE (4) <= bus_in_fifo_empty;
	
	--led_VALUE (7 downto 0) <= dds_ram_data_out (15 downto 8);
	
	
	-------- step the ram address to the next value when detect the pulse to step to next parameter ------
	
	process (dds_step_to_next_freq, dds_ram_reset)
		variable dds_step_count: integer range 0 to 1023:=0;
	begin
			if (dds_ram_reset = '1') then
				dds_step_count:=0;
			elsif (rising_edge(dds_step_to_next_freq)) then	
				dds_step_count := dds_step_count+1;
			end if;
			dds_ram_rdaddress<=CONV_STD_LOGIC_VECTOR(dds_step_count,10);
	end process;
	
	
	process (clk_system,dds_ram_reset)
		variable write_ram_address: integer range 0 to 2045:=0;
		variable ram_process_count: integer range 0 to 9:=0;
	begin
		----- reset ram -----
		----- This doesn't really reset the ram but only put the address to zero so that the next writing 
		----- from the fifo to the ram will start from the first address. Since each pulse will end with all zeros anyway
		----- it's ok to have old information in the ram. The execution will never get past the end line.
		if (dds_ram_reset = '1') then
			write_ram_address := 0;
			ram_process_count := 0;
		elsif rising_edge(clk_system) then
			case ram_process_count is
				--------- first two prepare and check whether there is anything in the fifo. This can be done by looking at the pin
				--------- fifo_pulser empty. 
				when 0 => fifo_dds_rd_clk <='1';
							 fifo_dds_rd_en <= '0';
							 dds_ram_wren <='0';
							 ram_process_count := 1;
				when 1 => fifo_dds_rd_clk <='0';
							 ram_process_count := 2;
				when 2 => if (bus_in_address = dip_in(2 downto 0)) then
								if (fifo_dds_empty = '1') then ---- '1' is empty. Go back to case 0 
									ram_process_count:=0; 
								else 
									ram_process_count := 3; --2 ---- if there's anything in the fifo, go to the next case
								end if;
							 else 
								ram_process_count:=0;
							 end if;
				-------- there's sth in the fifo ---------
				when 3 => fifo_dds_rd_en <= '1';
							 ram_process_count:=4;
				when 4 => fifo_dds_rd_clk <= '1'; ------------- read from fifo --------------
							 dds_ram_wren <='1';
							 dds_ram_wrclock <= '1';
							 ram_process_count:=5;
				when 5 => fifo_dds_rd_clk <= '0';
							 ram_process_count:=6;
				
				---------- prepare data and address that are about to be written to the ram------
				
				when 6 => dds_ram_wraddress <= CONV_STD_LOGIC_VECTOR(write_ram_address,11);
							 dds_ram_data_in <= fifo_dds_dout;
							 ram_process_count:=7;
				when 7 => dds_ram_wrclock <= '0'; ----------write to ram
							 ram_process_count:=8;
				when 8 => write_ram_address:=write_ram_address+1; ----- increase address by one
							 ram_process_count:=9;
				----- check again if the fifo is empty or not. Basically this whole process will
				----- keep writing to ram until fifo is empty.
				when 9 => if (fifo_dds_empty = '1') then 
								ram_process_count:=0;
							 else 
								ram_process_count:=3; 
							 end if;
			end case;
		end if;
	end process;
	
	
	
	PROCESS
		VARIABLE count_serial: INTEGER RANGE 0 to 9:=0;
	BEGIN
		WAIT UNTIL (clk_system'EVENT AND clk_system='0');
		CASE count_serial IS
			WHEN 0  => LED_OE <= '0'; LED_LE <= '0';
			WHEN 1  => LED_SDI <= LED_VALUE (7 DOWNTO 7);---- first----
			WHEN 2  => LED_SDI <= LED_VALUE (6 DOWNTO 6);
			WHEN 3  => LED_SDI <= LED_VALUE (5 DOWNTO 5);
			WHEN 4  => LED_SDI <= LED_VALUE (4 DOWNTO 4);
			WHEN 5  => LED_SDI <= LED_VALUE (3 DOWNTO 3);
			WHEN 6  => LED_SDI <= LED_VALUE (2 DOWNTO 2);
			WHEN 7  => LED_SDI <= LED_VALUE (1 DOWNTO 1);
			WHEN 8  => LED_SDI <= LED_VALUE (0 DOWNTO 0);LED_OE <= '0';LED_LE <= '1';---- last bit----
			WHEN 9 => LED_OE <= '0';LED_LE <= '1';
		END CASE;
		count_serial := count_serial +1;
		IF (count_serial = 9) THEN
			count_serial :=0;	
		END IF;
	END PROCESS;
	
	SINGLE_TONE0_DATA (63 DOWNTO 62) <= "00";
	SINGLE_TONE0_DATA (61 DOWNTO 48) <="11111111111111";
	SINGLE_TONE0_DATA (47 DOWNTO 32) <="0000000000000000";
	SINGLE_TONE0_DATA (31 DOWNTO 0)  <="01010000000000000000000000000000";
	
	SINGLE_TONE1_DATA (63 DOWNTO 62) <= "00";
	SINGLE_TONE1_DATA (61 DOWNTO 48) <="11111111111111";
	SINGLE_TONE1_DATA (47 DOWNTO 32) <="0000000000000000";
	SINGLE_TONE1_DATA (31 DOWNTO 0)  <="01000000000000000000000000000000";
	
	----------------------------------------------------------------------------------------------------
	----------------------- first write to DAC, then release parallel port to do frequency tuning ------	
	---------- It's running on 100 MHz to have fast update rate ----------------------------------------
	----------------------------------------------------------------------------------------------------
	
	PROCESS (clk_100)
		VARIABLE main_count: INTEGER range 0 to 5:=0;
	BEGIN
		IF (clk_100'event and clk_100='0') then
			CASE main_count IS
				WHEN 0 => parallel_data (13 downto 0) <= dds_ram_data_out (31 downto 18); -----set amplitude
							 parallel_data (15 downto 14) <= "00";
							 dac_wr_pin <= '0';
							 txen_pin <= '0'; ----- stop write freq
							 main_count:=1;
				WHEN 1 => dac_wr_pin <= '1'; -------------write to dac for amplitude
				          main_count:=2;
				WHEN 2 => dac_wr_pin <= '0'; -------------write to dac for amplitude
				          main_count:=3;
				WHEN 3 => parallel_data<=dds_ram_data_out(15 downto 0); ---------set frequency
							 dac_wr_pin <= '0'; ------------- stop write dac
							 main_count:=4;
				WHEN 4 => txen_pin <= '1'; -------write freq
							 main_count:=5;
				WHEN 5 => txen_pin <= '0'; -------write freq
							 main_count:=0;
				WHEN OTHERS => NULL;
			END CASE;
		END IF;
	END PROCESS;
	
--	PROCESS (clk_100)
--		VARIABLE main_count: INTEGER range 0 to 5:=0;
--	BEGIN
--		IF (clk_100'event and clk_100='0') then
--			CASE main_count IS
--				WHEN 0 => parallel_data (13 downto 0) <= dds_ram_data_out (31 downto 18); -----set amplitude
--							 dac_wr_pin <= '0';
--							 txen_pin <= '0';
--							 main_count:=1;
--				WHEN 1 => dac_wr_pin <= '1'; -------------write to dac for amplitude
--				          main_count:=2;
--				WHEN 2 => dac_wr_pin <= '0'; -------------stop write dac
--							 main_count:=3;
--				WHEN 3 => parallel_data<=dds_ram_data_out(15 downto 0); ---------set frequency
--							 dac_wr_pin <= '0';
--							 main_count:=4;
--				WHEN 4 => txen_pin <= '1'; -------write freq
--							 main_count:=5;
--				WHEN 5 => txen_pin <= '0'; -------stop write freq
--							 main_count:=0;
--				WHEN OTHERS => NULL;
--			END CASE;
--		END IF;
--	END PROCESS;
	                                                                                                      
	cs_pin<='0';
	
	reset_fpga<=bus_in_reset_dds_chip;
	profile_pin <= "000";
	
	----------- set lower bound freq here ----------------
	
	--FTW_DATA <="01000000000000000000000000000000"; ---- 200 MHz ----
	--FTW_DATA <="00100000000000000000000000000000"; ---- 100 MHz ----
	--FTW_DATA <="00001001100110011001100110011010"; ---- 30 MHz (+100 MHz tuning) for 80 MHz AOM
	--FTW_DATA <="00010011001100110011001100110100"; ---- 60 MHz (+100 MHz tuning) for 110 MHz AOM
	--FTW_DATA <="00110000000000000000000000000000"; ---- 150 MHz for 200 MHz AOM
	--FTW_DATA <="00110110011001100110011001100110"; ---- 170 MHz for 220 MHz AOM
	
	-- We can set the lower frequency using the dip switch. "00" is 80 MHz AO, "01" is 110 MHz AO, "10" is 200 MHz AO, "11" is 220 MHz AO ---
	
	FTW_DATA <= "00001001100110011001100110011010" WHEN dip_in (4 downto 3) = "00" ELSE
				   "00010011001100110011001100110100" WHEN dip_in (4 downto 3) = "01" ELSE
					"00110000000000000000000000000000" WHEN dip_in (4 downto 3) = "10" ELSE
					"00110110011001100110011001100110";
	
	---------------------parallel port control---------------
	CFR2_DATA (31 downto 25) <= "0000000"; ----Open
	CFR2_DATA (24 downto 12) <= "0010000000000";-----default
	CFR2_DATA (11 downto 4) <= "10000111";----parallel port configuration
	CFR2_DATA (3 downto 0) <= "1101";-----gain for freq tuning
	pargain_pin <= "10";
	--txen_pin <= '1';
	
	-------PLL control------
	
--	CFR3_DATA (31 downto 30) <= "00"; ----Open
--	CFR3_DATA (29 downto 16) <= "00010000111000";-----default
--	CFR3_DATA (15 downto 8) <= "11000001";----
--	CFR3_DATA (7 downto 1) <= "0100000";---- PLL divider
--	CFR3_DATA(0) <= '0';
	
	---- no pll -----
	CFR3_DATA (31 downto 30) <= "00"; ----Open
	CFR3_DATA (29 downto 16) <= "00011100111000";-----default
	CFR3_DATA (15 downto 8) <= "11000000";----
	CFR3_DATA (7 downto 1) <= "0000000";----
	CFR3_DATA(0) <= '0';

	------------------------ write instructions to DDS -------------------------------------
	PROCESS (clk_system,reset_fpga)
		VARIABLE int_bit_count: INTEGER range 0 to 7:=7;
		VARIABLE data_bit_count: INTEGER range 0 to 63:=63;
		VARIABLE main_count: INTEGER range 0 to 16:=0;
		VARIABLE sub_count: INTEGER range 0 to 1:=0;
		VARIABLE command_count: INTEGER range 0 to 99:=0;
		VARIABLE instruction: STD_LOGIC_VECTOR (7 downto 0);
		VARIABLE data_to_write: STD_LOGIC_VECTOR (63 downto 0);
	BEGIN
		IF (reset_fpga = '1') then
			main_count := 0;
			dds_reset_pin <= '1';
		ELSIF (clk_system'event and clk_system='0') then
			CASE main_count IS
				WHEN 0 => dds_reset_pin <= '0';
						  ioreset_pin<='1';
						  sclk_pin <='0';
						  ioup_pin <='0';
						  command_count := 0;
						  main_count := 1;
				WHEN 1 => ioreset_pin<='1';
						  sclk_pin <='0';
						  ioup_pin <='0';
						  main_count := 2;
				WHEN 2 => ioreset_pin<='0';
			           sclk_pin <='0';
						  ioup_pin <='0';
						  main_count := 3;
				WHEN 3 => sclk_pin <='0'; --------- ready to clock data
						  IF (command_count = 0) THEN
								instruction:=CFR2_OP;
								data_to_write (31 downto 0):=CFR2_DATA;
								data_bit_count:=31;
								main_count := 4;
						  ELSIF (command_count = 1) THEN
								instruction:=CFR3_OP;
								data_to_write (31 downto 0):=CFR3_DATA;
								data_bit_count:=31;
								main_count := 4;
						  ELSIF (command_count = 2) THEN
								instruction:=FTW_OP;
								data_to_write (31 downto 0):=FTW_DATA;
								data_bit_count:=31;
								main_count := 4;							
						  ELSIF (command_count = 3) THEN
								instruction:=SINGLE_TONE0_OP;
								data_to_write:=SINGLE_TONE0_DATA;
								data_bit_count:=63;
								main_count := 4;								
						  ELSIF (command_count = 4) THEN
								instruction:=SINGLE_TONE1_OP;
								data_to_write:=SINGLE_TONE1_DATA;
								data_bit_count:=63;
								main_count := 4;	
						  ELSIF (command_count = 5) THEN
							   main_count:=7;
						  END IF;		  
				-------start clocking data-------
				-------CLOCK instruction bit-----
				WHEN 4 => IF (sub_count = 0) THEN
								sclk_pin <='0';
								sdio_pin<=INSTRUCTION(int_bit_count);
								sub_count:=1;
							 ELSIF (sub_count=1) THEN
								IF (int_bit_count = 0) THEN
									main_count := 5;
									sclk_pin<='1';
									sub_count := 0;
									int_bit_count := 7;
								ELSE
									sclk_pin<='1';
									sub_count:=0;
									int_bit_count:=int_bit_count-1;
								END IF;
							 END IF;
				--------CLOCK Data bit-----------
				WHEN 5 => IF (sub_count = 0) THEN
								sclk_pin <='0';
								sdio_pin<=data_to_write(data_bit_count);
								sub_count:=1;
							 ELSIF (sub_count=1) THEN
								IF (data_bit_count = 0) THEN
									main_count := 6;
									sclk_pin<='1';
									sub_count := 0;
								ELSE
									sclk_pin<='1';
									sub_count:=0;
									data_bit_count:=data_bit_count-1;
								END IF;
							 END IF;
				WHEN 6 => sclk_pin<='0';
							 command_count:=command_count+1;
							 main_count :=3;
				WHEN 7 to 10 => ioup_pin <= '1';
							 main_count :=main_count+1;
				WHEN 11 to 14 => ioup_pin <='0';
							 main_count :=main_count+1;
				WHEN 15 => main_count:=16;
				WHEN OTHERS => NULL;
			END CASE;
		END IF;
	END PROCESS;
	
	---------- unused pins ------
	clk_out <= 'Z';
	drover_pin <= 'Z';
	drctl_pin <= 'Z';
	drhold_pin <= 'Z';
	osk_pin <= 'Z';

end behaviour;
