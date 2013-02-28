library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.std_logic_arith.all;
use IEEE.std_logic_misc.all;
use IEEE.std_logic_unsigned.all;
use IEEE.STD_LOGIC_1164.ALL;

entity ddr2_test is

  PORT (
		clk : in STD_LOGIC;
		reset: in STD_LOGIC;
		writes_en: in STD_LOGIC;
		reads_en: in STD_LOGIC;
		calib_done: in STD_LOGIC;
		ram_full: out STD_LOGIC;
		
		---- input buffer
		ib_re: out STD_LOGIC;
		ib_data: in STD_LOGIC_VECTOR(63 downto 0);
		ib_count: in STD_LOGIC_VECTOR(8 downto 0);
		ib_valid: in STD_LOGIC;
		ib_empty: in STD_LOGIC;
		---- output buffer
		ob_we: buffer STD_LOGIC;
		ob_data: out STD_LOGIC_VECTOR(63 downto 0);
		ob_count: in STD_LOGIC_VECTOR(8 downto 0);
		
		---- connection to SDRAM wrapper
		p0_rd_en_o: out STD_LOGIC;
		p0_rd_empty: in STD_LOGIC;
		p0_rd_data: in STD_LOGIC_VECTOR(31 downto 0);
	
		p0_cmd_full: in STD_LOGIC;
		p0_cmd_en: buffer STD_LOGIC;
		p0_cmd_instr: buffer STD_LOGIC_VECTOR(2 downto 0);
		p0_cmd_byte_addr: out STD_LOGIC_VECTOR(29 downto 0);
		p0_cmd_bl_o: out STD_LOGIC_VECTOR(5 downto 0);
		p0_wr_full: in STD_LOGIC;
		p0_wr_en: out STD_LOGIC;
		p0_wr_data: out STD_LOGIC_VECTOR(31 downto 0);
		p0_wr_mask: out STD_LOGIC_VECTOR(3 downto 0)	
  );
  
end ddr2_test;

architecture Behavioral of ddr2_test is
	
	constant BURST_LEN : integer := 2;  ----- number of 32 bit words per command. Must be a multiple of 2
	
	signal rd_fifo_afull: STD_LOGIC;
	signal cmd_byte_addr_wr: STD_LOGIC_VECTOR(29 downto 0);
	signal cmd_byte_addr_rd: STD_LOGIC_VECTOR(29 downto 0);
	signal burst_cnt: STD_LOGIC_VECTOR(5 downto 0);
	signal write_mode: STD_LOGIC;
	signal read_mode: STD_LOGIC;
	signal reset_d: STD_LOGIC;
	signal reads_queued: STD_LOGIC_VECTOR(10 downto 0);
	signal ob_used: STD_LOGIC_VECTOR(10 downto 0);
	
	TYPE STATE_TYPE IS (s_idle, s_write1, s_write2, s_write3, s_write4, s_read1, s_read2, s_read3, s_read4, s_read5);
	signal state : STATE_TYPE;
	

begin
	p0_wr_mask <= "0000";
	p0_cmd_bl_o <= CONV_STD_LOGIC_VECTOR(BURST_LEN-1,6);
	
	process (clk)
	BEGIN
		IF (clk'EVENT and clk = '1') THEN
			write_mode <= writes_en;
			read_mode <= reads_en;
			reset_d <= reset;
		END IF;
	END PROCESS;
	
	process (reset_d, clk)
	BEGIN
		IF (reset_d = '1') THEN
			state           <= s_idle;
			burst_cnt       <= "000000";
			reads_queued    <= "00000000000";
			ob_used         <= "00000000000";
			cmd_byte_addr_wr  <= "000000000000000000000000000000";
			cmd_byte_addr_rd  <= "000000000000000000000000000000";
			p0_cmd_instr <= "000";
			p0_cmd_byte_addr <= "000000000000000000000000000000";
			ram_full <= '0';
		ELSIF (clk'EVENT and clk = '1') THEN
			p0_cmd_en  <= '0';
			p0_wr_en <= '0';
			ib_re <= '0';
			p0_rd_en_o <= '0';
			ob_we <= '0';
			IF ((p0_cmd_en & p0_cmd_instr) = "1001") THEN
				reads_queued <= CONV_STD_LOGIC_VECTOR(CONV_INTEGER(UNSIGNED (reads_queued))+ BURST_LEN,11);
			END IF;
			IF (ob_we = '1') THEN
				reads_queued <= CONV_STD_LOGIC_VECTOR(CONV_INTEGER(UNSIGNED (reads_queued))-2,11);
			END IF;
			ob_used <= CONV_STD_LOGIC_VECTOR(CONV_INTEGER(UNSIGNED(reads_queued(10 downto 1))) + CONV_INTEGER(UNSIGNED(ob_count)),11);
			
			CASE state IS
			
				WHEN s_idle =>
					burst_cnt <= CONV_STD_LOGIC_VECTOR(BURST_LEN,6);
					---- BURST_LEN is half because the input_buffer is 64 bit word --- 32 * 32 bit = 16 * 64 bit
					IF ((calib_done = '1') AND (write_mode = '1') AND (CONV_INTEGER(UNSIGNED(ib_count))>=BURST_LEN/2)) THEN  
						IF (cmd_byte_addr_wr(26 downto 1) = "11111111111111111111110000") THEN
							state <= s_idle;
							ram_full <= '1';
						ELSE
							state <= s_write1;
						END IF;
					ELSIF ((calib_done = '1') AND (read_mode = '1') AND (CONV_INTEGER(UNSIGNED(ob_used))<440)) THEN
						state <= s_read1;
					END IF;
					
				WHEN s_write1 =>
					state <= s_write2;
					ib_re <= '1';
					
				WHEN s_write2 =>
					IF (ib_valid = '1') THEN
						p0_wr_data <= ib_data(31 downto 0);
						p0_wr_en <= '1';
						burst_cnt <= CONV_STD_LOGIC_VECTOR(CONV_INTEGER(UNSIGNED (burst_cnt))-2,6);
						state <= s_write3;
					END IF;
				
				WHEN s_write3 =>
					p0_wr_data <= ib_data(63 downto 32);
					p0_wr_en <= '1';
					IF (burst_cnt = "000000") THEN
						state <= s_write4;
					ELSE
						state <= s_write1;
					END IF;
					
				WHEN s_write4 =>
					p0_cmd_en <= '1';
					p0_cmd_byte_addr <= cmd_byte_addr_wr;
					cmd_byte_addr_wr <= CONV_STD_LOGIC_VECTOR(CONV_INTEGER(UNSIGNED (cmd_byte_addr_wr))+ 4*BURST_LEN,30);
					p0_cmd_instr <= "000";
					state <= s_idle;
				
				WHEN s_read1 =>
					p0_cmd_byte_addr <= cmd_byte_addr_rd;
					cmd_byte_addr_rd <= CONV_STD_LOGIC_VECTOR(CONV_INTEGER(UNSIGNED (cmd_byte_addr_rd))+ 4*BURST_LEN,30);
					p0_cmd_instr <= "001";
					p0_cmd_en <= '1';
					state <= s_read2;
					
				WHEN s_read2 =>
					IF (p0_rd_empty = '0') THEN
						p0_rd_en_o <= '1';
						state <= s_read3;
					END IF;
					
				WHEN s_read3 =>
					ob_data(31 downto 0) <= p0_rd_data;
					IF (p0_rd_empty = '0') THEN
						p0_rd_en_o <= '1';
						state <= s_read4;
					END IF;
				
				WHEN s_read4 =>
					ob_data(63 downto 32) <= p0_rd_data;
					ob_we <= '1';
					burst_cnt <= CONV_STD_LOGIC_VECTOR(CONV_INTEGER(UNSIGNED (burst_cnt))-2,6);
					state <= s_read5;
					
				WHEN s_read5 =>
					IF (burst_cnt = "000000") THEN
						state <= s_idle;
					ELSE
						state <= s_read2;
					END IF;
			END CASE;
		END IF;
	END PROCESS;
			
end Behavioral;

