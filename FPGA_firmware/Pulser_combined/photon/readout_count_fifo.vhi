
-- VHDL Instantiation Created from source file readout_count_fifo.vhd -- 16:46:32 07/06/2012
--
-- Notes: 
-- 1) This instantiation template has been automatically generated using types
-- std_logic and std_logic_vector for the ports of the instantiated module
-- 2) To use this template to instantiate this entity, cut-and-paste and then edit

	COMPONENT readout_count_fifo
	PORT(
		rst : IN std_logic;
		wr_clk : IN std_logic;
		rd_clk : IN std_logic;
		din : IN std_logic_vector(31 downto 0);
		wr_en : IN std_logic;
		rd_en : IN std_logic;          
		dout : OUT std_logic_vector(15 downto 0);
		full : OUT std_logic;
		empty : OUT std_logic;
		rd_data_count : OUT std_logic_vector(10 downto 0)
		);
	END COMPONENT;

	Inst_readout_count_fifo: readout_count_fifo PORT MAP(
		rst => ,
		wr_clk => ,
		rd_clk => ,
		din => ,
		wr_en => ,
		rd_en => ,
		dout => ,
		full => ,
		empty => ,
		rd_data_count => 
	);


