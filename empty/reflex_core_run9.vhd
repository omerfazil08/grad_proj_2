-- REFLEX ENGINE GENERATED: 2026-01-16 13:05:40.130849
-- Run ID: 9 | Penalty: 9.0
-- Label: SWEEP_WINNER
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reflex_core_run9 is
    Port ( clk : in STD_LOGIC;
           sensor_stream : in STD_LOGIC_VECTOR(15 downto 0);
           alarm_out : out STD_LOGIC);
end reflex_core_run9;

architecture Behavioral of reflex_core_run9 is
    signal w : std_logic_vector(55 downto 0);
begin
    w(15 downto 0) <= sensor_stream;
    w(16) <= not(w(9) or w(12));
    w(17) <= not(w(14) and w(7));
    w(18) <= w(17);
    w(19) <= not w(2);
    w(20) <= not(w(9) and w(11));
    w(21) <= w(17) and w(20);
    w(22) <= w(6) or w(14);
    w(23) <= w(11);
    w(24) <= w(16);
    w(25) <= not(w(24) or w(8));
    w(26) <= not(w(18) and w(17));
    w(27) <= w(22) and w(10);
    w(28) <= w(6) xor w(8);
    w(29) <= not w(13);
    w(30) <= w(15) or w(29);
    w(31) <= w(5) and w(6);
    w(32) <= w(12) and w(27);
    w(33) <= not(w(23) and w(3));
    w(34) <= w(12) xor w(30);
    w(35) <= not(w(26) and w(31));
    w(36) <= w(31);
    w(37) <= w(13);
    w(38) <= not(w(21) or w(12));
    w(39) <= w(18) and w(12);
    w(40) <= not(w(31) and w(13));
    w(41) <= w(38) xor w(10);
    w(42) <= w(14) xor w(36);
    w(43) <= w(30) and w(31);
    w(44) <= w(9) and w(14);
    w(45) <= w(14) and w(33);
    w(46) <= not(w(2) or w(18));
    w(47) <= not(w(2) or w(3));
    w(48) <= not(w(25) or w(38));
    w(49) <= w(48) and w(23);
    w(50) <= not(w(13) and w(15));
    w(51) <= w(34);
    w(52) <= w(24) xor w(11);
    w(53) <= not w(14);
    w(54) <= not(w(50) or w(33));
    w(55) <= w(4) or w(14);
    alarm_out <= w(27);
end Behavioral;