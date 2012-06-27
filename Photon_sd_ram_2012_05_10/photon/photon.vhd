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
		------- PMT input from the level translator. Note that the PMT pulse width is roughly 5-7 ns ----
		pmt_input : in 	STD_LOGIC;
		------- Logic In/Out ------
		logic_out: out STD_LOGIC_VECTOR (31 downto 0);
		logic_in:  in STD_LOGIC_VECTOR (3 downto 0);
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
	
	----- FIFO for photon data -------
	----- The time stamp of the photon is recorded into the fifo and ready to be read from the PC ------------
	----- Due to the limitation in RAM size on-board, the number of photon tagged can be only 2^15 = 32768 ---
	
	component fifo_photon PORT (
		rst : IN STD_LOGIC;
		wr_clk : IN STD_LOGIC;
		rd_clk : IN STD_LOGIC;
		din : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
		wr_en : IN STD_LOGIC;
		rd_en : IN STD_LOGIC;
		dout : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
		full : OUT STD_LOGIC;
		empty : OUT STD_LOGIC;
		rd_data_count : OUT STD_LOGIC_VECTOR(15 DOWNTO 0));
	end component;
	
	----- block ram to store the pulses ---------------------------------------------------------------------
	----- The pulse data is first written into fifo (below). Then the fifo will transfer the data to ram. ----
	
	component pulser_ram PORT (
		clka : IN STD_LOGIC;
		wea : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
		addra : IN STD_LOGIC_VECTOR(9 DOWNTO 0);
		dina : IN STD_LOGIC_VECTOR(63 DOWNTO 0);
		clkb : IN STD_LOGIC;
		addrb : IN STD_LOGIC_VECTOR(9 DOWNTO 0);
		doutb : OUT STD_LOGIC_VECTOR(63 DOWNTO 0));
	end component;
	
	------ fifo to from pc to ram to store pulse ----
	
	component pulse_fifo PORT (
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
	
	-------- normal pmt fifo ---------
	
	component normal_pmt_fifo PORT (
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
	
	-- Target interface bus:
	signal ti_clk    : STD_LOGIC;
	signal ok1       : STD_LOGIC_VECTOR(30 downto 0);
	signal ok2       : STD_LOGIC_VECTOR(16 downto 0);
	signal ok2s      : STD_LOGIC_VECTOR(17*6-1 downto 0);

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
	
	------ output data to PC ------
	signal ep21wire		  : STD_LOGIC_VECTOR(15 downto 0):="0000000000000000";
	signal ep22wire		  : STD_LOGIC_VECTOR(15 downto 0):="0000000000000000";
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
	
	signal bs_in, bs_out   : STD_LOGIC;
	signal bs_in_dds, bs_out_dds   : STD_LOGIC;
	
	--- CLOCKs -----

	--- clk 100 MHz from PLL.
	signal clk_100         : STD_LOGIC;
	--- clk 200 MHz from PLL to sample the input PMT signal. Any slower clock will miss the pulse ---
	signal clk_200         : STD_LOGIC;
	--- clk 20 MHz from PLL. Not used for anything right now ----
	signal clk_20          : STD_LOGIC; 

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
	signal	pulser_ram_addra 				: STD_LOGIC_VECTOR(9 DOWNTO 0);
	signal	pulser_ram_dina 				: STD_LOGIC_VECTOR(63 DOWNTO 0);
	signal	pulser_ram_clkb 				: STD_LOGIC;
	signal	pulser_ram_addrb 				: STD_LOGIC_VECTOR(9 DOWNTO 0);
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
	

begin
----------------------------------------------------------------------------

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
led(3 downto 0) <= "1111";


---============= DDS stuff ==============================
---------------------------------------------------------

dds_logic_data_out <= fifo_dds_dout;
fifo_dds_rd_clk <= dds_logic_fifo_rd_clk;
fifo_dds_rd_en <= dds_logic_fifo_rd_en;
dds_logic_fifo_empty <= fifo_dds_empty;
dds_logic_ram_reset <= master_logic(19) or ep40wire(4); -----------dds reset----------
dds_logic_step_to_next_value <= master_logic(18) or ep40wire(5);
dds_logic_reset_dds_chip <= ep40wire(6);

dds_logic_address <= ep04wire(2 downto 0); ---------------set dds channel

----------------------------------------------------------

--	process (clk_200)
--	begin
--		IF rising_edge(clk_200) THEN
--			pmt_synced <= pmt_input;
--		END IF;
--	END PROCESS;
	
----------------------------------------------------------------------
----------- general pll. This generated 200 MHz and 20 MHz from 100 MHz ------
pll: clk_pll_100_in_200_out port map(

	-- Clock in ports
		CLK_IN1 => clk1,
   -- Clock out ports
		CLK_OUT1 => clk_200,
		CLK_OUT2 => clk_100,
		CLK_OUT3 => clk_20);
		
-----------------------------------------------------------------------------------------------------		
----------- this fifo is to store data from the pc before writing to the block ram for pulser -------
----------- this fifo is first-word-fall-through!!! -------------------------------------------------
-----------------------------------------------------------------------------------------------------

fifo2: pulse_fifo port map(
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

ram1: pulser_ram port map (
		clka => pulser_ram_clka,
		wea => pulser_ram_wea,
		addra => pulser_ram_addra,
		dina => pulser_ram_dina,
		clkb => pulser_ram_clkb,
		addrb => pulser_ram_addrb,
		doutb => pulser_ram_doutb);
		
	process (clk_100,pulser_ram_reset)
		variable write_ram_address: integer range 0 to 1023:=0;
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
				
				when 5 => pulser_ram_addra <= CONV_STD_LOGIC_VECTOR(write_ram_address,10);
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
		variable ram_read_address: integer range 0 to 1023:=0;
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
							   ram_process_count := ram_process_count + 1;
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
			pulser_ram_addrb<=conv_std_logic_vector(ram_read_address,10);
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
----- 5 ------ 729Switch
----- 6 ------ 110DPlist
----- 7 ------ camera: P13
----- 8
----- 9
----- 16 ----- pmt counter trigger for differential mode (DiffCountTrigger)
----- 17 ----- time resolved photon counting enable (TimeResolvedCount)
----- 18 ----- dds step to next value
----- 19 ----- reset dds

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
------------------------------------------------------------------------------------------
----- If more channels are needed, just copy above ---------------------------------------
	LOGIC_OUT(31 downto 10) <= master_logic(31 downto 10);

---- This is the data that indicates the number of photon tagged stored in the fifo ------
----- It will be twice the number of photon tagged because each photon tag requires 32 bit
----- but the fifo output is 16 bit wide
						 
ep22wire <= fifo_photon_rd_data_count;

----------- Get flag from epwire  ----------------
----------- ep00wire(0) is the normal pmt or differential pmt mode -------
pulser_counter_reset <= ep40wire(0);	
pulser_ram_reset <= ep40wire(1);	
pulser_infinite_loop <= ep00wire(1);			
pulser_start_bit <= ep00wire(2);	

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
		else
			ep21wire <= "0000000000000000";
		end if;
	end if;
end process;
				
----------- this fifo is for buffering the photon tagging data, when it's not enough the plan is to write to sdram----
---------- The logic(27) is to indicate which in the pulse sequece for the photon to get tagged. This is to ------
---------- have better control when there is time where no time resolved photon counting is needed ------

fifo_photon_wr_en <= master_logic(17);
------------------- to have the writing clocked tied to the pmt ---------------------------
--fifo_photon_wr_clk <= pmt_synced;

normal_pmt_pipe_out_valid <= '1';
time_resolved_pipe_out_valid <= '1';
		
fifo1: fifo_photon port map (
		rst=>fifo_photon_rst,
		wr_clk=>fifo_photon_wr_clk,
		rd_clk=>ti_clk,
		din=> fifo_photon_din,
		wr_en=> fifo_photon_wr_en,
		rd_en=> time_resolved_pipe_out_read, 
		--- the fifo is configured in a standard way that data is present one cycle after rd_en is asserted
		--- this is coincide with the way pipe_out_read is also asserted
		dout=> time_resolved_pipe_out_data,
		full=> fifo_photon_full,
		empty=> fifo_photon_empty,
		rd_data_count=>fifo_photon_rd_data_count);

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
	
	--------- LED -------
	
	--led(5 DOWNTO 1) <= NOT normal_pmt_rd_data_count(6 DOWNTO 2);
	--led(0) <= not normal_pmt_count_trigger;
	--led(7) <= not normal_pmt_full;
	--led(6) <= not master_logic(0);
	
	normal_pmt_block_aval <= '0' WHEN normal_pmt_rd_data_count = "00000000000" ELSE '1';
	
	------ generate timing sequece -------
	------ write to fifo at the beginning of the count trigger ----
	------ the dead time that we can't count is very low and can be ignored ------
	
	process (clk_100, normal_pmt_count_trigger)   ----count_trigger_active_high----
		variable count: integer range 0 to 10:=0;
		variable wr_clk_var: STD_LOGIC:='0';
		variable wr_en_var: STD_LOGIC:='0';
		variable fifo_data_var:STD_LOGIC_VECTOR(31 DOWNTO 0):="00000000000000000000000000000000";
		variable pmt_count_reset_var: STD_LOGIC:='0';
	begin
		if (normal_pmt_count_trigger = '0') then
			count:=0;
		elsif (rising_edge(clk_100) and normal_pmt_count_trigger = '1') then
			case count IS
				WHEN 0 => wr_clk_var := '0';
							 wr_en_var := '0';
							 fifo_data_var (30 DOWNTO 0) := CONV_STD_LOGIC_VECTOR(pmt_count,31);
							 fifo_data_var (31) := '0' WHEN ep00wire(0) = '0' ELSE 
														  '0'	WHEN (master_logic(0) = '1' AND ep00wire(0) = '1') ELSE 
														  '1';
							 pmt_count_reset_var:='0';
							 count:=count+1;
				WHEN 1 => count:=count+1;
				WHEN 2 => wr_en_var:='1';
							 count:=count+1;
				WHEN 3 => count:=count+1;
				WHEN 4 => wr_clk_var:='1';
							 count:=count+1;
				WHEN 5 => count:=count+1;
				WHEN 6 => wr_clk_var:='0';
							 wr_en_var:='0';
							 count:=count+1;
				WHEN 7 => count:=count+1;
				WHEN 8 => pmt_count_reset_var:='1';
							 count:=count+1;
				WHEN 9 => count:=count+1;
				WHEN 10 => pmt_count_reset_var:='0';
				WHEN OTHERS => NULL;
			end case;	 
			normal_pmt_wr_clk<=wr_clk_var;
			normal_pmt_wr_en<=wr_en_var;
			normal_pmt_fifo_data<=fifo_data_var;
			pmt_count_reset<=pmt_count_reset_var;
		end if;
	end process;
	
	-------- count pmt by incresaing the value of pmt_count every time pmt_synced edge is detected ---------
	
	
	process (pmt_count_reset, pmt_synced)
	begin
		if (pmt_count_reset = '1') then
			pmt_count<=0;
		elsif (rising_edge(pmt_synced)) then
			pmt_count<=pmt_count+1;
		end if;
	end process;
	
	
	-- FIFO for normal PMT ---------------
	-- write in 32 bit, read out 16 bit --
	
	fifo3: normal_pmt_fifo port map (rst => normal_pmt_fifo_reset,
													wr_clk => normal_pmt_wr_clk,
													rd_clk =>ti_clk,
													din => normal_pmt_fifo_data,
													wr_en => normal_pmt_wr_en,
													rd_en =>normal_pmt_pipe_out_read, 
													dout => normal_pmt_pipe_out_data,
													full =>normal_pmt_full,
													empty =>normal_pmt_empty,
													rd_data_count=>normal_pmt_rd_data_count
													);

-- Instantiate the okHost and connect endpoints.
 
okHI : okHost port map (hi_in=>hi_in, hi_out=>hi_out, hi_inout=>hi_inout, hi_aa=>hi_aa, ti_clk=>ti_clk, ok1=>ok1, ok2=>ok2);
okWO : okWireOR    generic map (N=>6) port map (ok2=>ok2, ok2s=>ok2s);
wi00 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"00", ep_dataout=>ep00wire);
wi01 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"01", ep_dataout=>ep01wire);
wi02 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"02", ep_dataout=>ep02wire);
wi03 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"03", ep_dataout=>ep03wire);
wi04 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"04", ep_dataout=>ep04wire);
wi05 : okWireIn    port map (ok1=>ok1,                                  ep_addr=>x"05", ep_dataout=>ep05wire);
ep40 : okTriggerIn  port map (ok1=>ok1,                                  ep_addr=>x"40", ep_clk=>clk_100, ep_trigger=>ep40wire);
wo21 : okWireOut   port map (ok1=>ok1, ok2=>ok2s( 1*17-1 downto 0*17 ), ep_addr=>x"21", ep_datain=>ep21wire);
wo22 : okWireOut   port map (ok1=>ok1, ok2=>ok2s( 4*17-1 downto 3*17 ), ep_addr=>x"22", ep_datain=>ep22wire);
ep80 : okBTPipeIn  port map (ok1=>ok1, ok2=>ok2s( 2*17-1 downto 1*17 ), ep_addr=>x"80", 
                             ep_write=>pipe_in_write, ep_blockstrobe=>bs_in, ep_dataout=>pipe_in_data, ep_ready=>pipe_in_ready);
ep81 : okBTPipeIn  port map (ok1=>ok1, ok2=>ok2s( 6*17-1 downto 5*17 ), ep_addr=>x"81", 
                             ep_write=>pipe_in_write_dds, ep_blockstrobe=>bs_in_dds, ep_dataout=>pipe_in_data_dds, ep_ready=>pipe_in_ready_dds);
----time resolved----
epA0 : okBTPipeOut port map (ok1=>ok1, ok2=>ok2s( 3*17-1 downto 2*17 ), ep_addr=>x"A0", 
                             ep_read=>time_resolved_pipe_out_read, ep_blockstrobe=>bs_out, ep_datain=>time_resolved_pipe_out_data, ep_ready=>time_resolved_pipe_out_valid);
----normal pmt ----
epA1 : okBTPipeOut port map (ok1=>ok1, ok2=>ok2s( 5*17-1 downto 4*17 ), ep_addr=>x"A1", 
                             ep_read=>normal_pmt_pipe_out_read, ep_blockstrobe=>bs_out, ep_datain=>normal_pmt_pipe_out_data, ep_ready=>normal_pmt_pipe_out_valid);

end arch;