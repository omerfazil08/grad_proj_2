-- REFLEX ENGINE: INNER_RACE FAULT DETECTOR
-- GENERATED: 2026-01-18 18:53:40.052074
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reflex_core_inner_race is
    Port ( clk : in STD_LOGIC;
           sensor_stream : in STD_LOGIC_VECTOR(15 downto 0);
           alarm_out : out STD_LOGIC);
end reflex_core_inner_race;

architecture Behavioral of reflex_core_inner_race is
    signal w : std_logic_vector(55 downto 0);
begin
    w(15 downto 0) <= sensor_stream;
    w(16) <= not w(12);
    w(17) <= w(4) or w(9);
    w(18) <= w(10) or w(5);
    w(19) <= not(w(2) or w(11));
    w(20) <= w(1) xor w(17);
    w(21) <= not(w(16) and w(12));
    w(22) <= not w(8);
    w(23) <= w(3);
    w(24) <= w(0) xor w(19);
    w(25) <= w(17) or w(18);
    w(26) <= w(13) or w(0);
    w(27) <= w(5);
    w(28) <= w(26) or w(14);
    w(29) <= not(w(3) or w(1));
    w(30) <= w(18) or w(13);
    w(31) <= w(14) xor w(2);
    w(32) <= not(w(23) and w(20));
    w(33) <= w(25) and w(28);
    w(34) <= w(33);
    w(35) <= w(0) or w(17);
    w(36) <= w(30) or w(14);
    w(37) <= not w(34);
    w(38) <= w(8) xor w(36);
    w(39) <= w(25) and w(1);
    w(40) <= not(w(29) or w(24));
    w(41) <= w(6) xor w(25);
    w(42) <= w(12) and w(30);
    w(43) <= w(33) or w(39);
    w(44) <= w(18);
    w(45) <= not w(15);
    w(46) <= not(w(14) or w(16));
    w(47) <= w(16) or w(35);
    w(48) <= w(7);
    w(49) <= not w(9);
    w(50) <= w(22) xor w(27);
    w(51) <= not(w(50) and w(19));
    w(52) <= w(43) xor w(21);
    w(53) <= not(w(52) and w(41));
    w(54) <= w(7);
    w(55) <= not(w(14) or w(14));
    alarm_out <= w(43);
end Behavioral;