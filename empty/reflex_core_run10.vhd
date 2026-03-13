-- REFLEX ENGINE GENERATED: 2026-01-14 05:12:19.147164
-- Run ID: 10 | Penalty: 10.0
-- Label: SWEEP_WINNER
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reflex_core_run10 is
    Port ( clk : in STD_LOGIC;
           sensor_stream : in STD_LOGIC_VECTOR(15 downto 0);
           alarm_out : out STD_LOGIC);
end reflex_core_run10;

architecture Behavioral of reflex_core_run10 is
    signal w : std_logic_vector(55 downto 0);
begin
    w(15 downto 0) <= sensor_stream;
    w(16) <= not(w(1) and w(3));
    w(17) <= not(w(11) and w(12));
    w(18) <= not(w(6) or w(5));
    w(19) <= not(w(1) or w(6));
    w(20) <= not(w(1) and w(13));
    w(21) <= w(19);
    w(22) <= w(10) and w(3);
    w(23) <= w(17) xor w(8);
    w(24) <= not(w(17) or w(15));
    w(25) <= w(1) or w(9);
    w(26) <= not w(18);
    w(27) <= w(18);
    w(28) <= w(27) and w(2);
    w(29) <= w(26) xor w(6);
    w(30) <= w(24);
    w(31) <= not(w(27) and w(25));
    w(32) <= w(7) and w(31);
    w(33) <= not w(25);
    w(34) <= not(w(28) and w(0));
    w(35) <= w(15) and w(33);
    w(36) <= not w(32);
    w(37) <= w(14) xor w(22);
    w(38) <= w(9) and w(10);
    w(39) <= not w(10);
    w(40) <= w(19);
    w(41) <= not(w(7) or w(39));
    w(42) <= not(w(31) and w(35));
    w(43) <= not w(4);
    w(44) <= not w(32);
    w(45) <= w(1);
    w(46) <= w(1) xor w(36);
    w(47) <= w(40);
    w(48) <= not(w(16) or w(28));
    w(49) <= not(w(39) and w(30));
    w(50) <= w(43) or w(6);
    w(51) <= not(w(40) or w(3));
    w(52) <= w(16) or w(43);
    w(53) <= not(w(17) or w(34));
    w(54) <= w(8) and w(28);
    w(55) <= w(36) or w(13);
    alarm_out <= w(48);
end Behavioral;