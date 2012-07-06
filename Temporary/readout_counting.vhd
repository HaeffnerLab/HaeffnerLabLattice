-- Readout Count Data --
signal	pmt_readout_count: INTEGER RANGE 0 TO 2147483647:=0;
signal	readout_count_start_trigger : STD_LOGIC := '0';
signal	readout_count_stop_trigger : STD_LOGIC := '0';

-------- count readout counts by incresaing the value of pmt_readout_count every time pmt_synced edge is detected ---------
process (readout_count_start_trigger, pmt_synced)
begin
	if rising_edge(readout_count_start_trigger) then
		pmt_readout_count<=0;
	elsif (rising_edge(pmt_synced)) then
		pmt_readout_count<=pmt_readout_count+1;
	end if;
end process;

---- process for counting during readout: 
---- start trigger resets the counting of pmt_readout_count
---- stop trigger write the result to fifo

process (clk_100, readout_count_start_trigger, readout_count_stop_trigger)
	variable count: integer range 0 to 7:=0;
	variable wr_clk_var: STD_LOGIC:='0';
	variable wr_en_var: STD_LOGIC:='0';
	variable fifo_data_var:STD_LOGIC_VECTOR(31 DOWNTO 0):="00000000000000000000000000000000";
begin
	if (readout_count_start_trigger = '0') then
		count:=0;
	elsif (rising_edge(clk_100) and readout_count_stop_trigger = '1') then
		case count IS
			WHEN 0 => 
				wr_clk_var := '0';
				wr_en_var := '0';
				fifo_data_var (31 DOWNTO 0) := CONV_STD_LOGIC_VECTOR(pmt_readout_count,32);
				count:=count+1;
			WHEN 1 => 
				count:=count+1;
			WHEN 2 => 
				wr_en_var:='1';
				count:=count+1;
			WHEN 3 =>
				count:=count+1;
			WHEN 4 =>
				wr_clk_var:='1';
				count:=count+1;
			WHEN 5 => 
				count:=count+1;
			WHEN 6 => 
				wr_clk_var:='0';
				wr_en_var:='0';
				count:=count+1;
			WHEN OTHERS => NULL;
		end case;	 
		readout_count_wr_clk<=wr_clk_var;
		readout_count_wr_en<=wr_en_var;
		readout_count_fifo_data<=fifo_data_var;
	end if;
end process;

process (ti_clk)
begin
	if rising_edge(ti_clk) then
		if (ep00wire(7 downto 5) = "000") Then
			ep21wire <= pulser_flag_register;
		elsif (ep00wire(7 downto 5) = "001") then
			ep21wire <= seq_count_bit;
		elsif (ep00wire(7 downto 5) = "010") then
			ep21wire(10 downto 0) <= normal_pmt_rd_data_count;
		elsif (ep00wire(7 downto 5) = "011") then
			ep21wire(10 downto 0) <= readout_count_rd_data_count;
		else
			ep21wire <= "0000000000000000";
		end if;
	end if;
end process;