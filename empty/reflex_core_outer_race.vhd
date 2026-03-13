-- REFLEX ENGINE: OUTER_RACE FAULT DETECTOR
-- GENERATED: 2026-01-18 02:41:42.092154
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reflex_core_outer_race is
    Port ( clk : in STD_LOGIC;
           sensor_stream : in STD_LOGIC_VECTOR(15 downto 0);
           alarm_out : out STD_LOGIC);
end reflex_core_outer_race;

architecture Behavioral of reflex_core_outer_race is
    signal w : std_logic_vector(55 downto 0);
begin
    w(15 downto 0) <= sensor_stream;
    w(16) <= w(10);
    w(17) <= w(3) xor w(14);
    w(18) <= not(w(17) and w(12));
    w(19) <= w(1) or w(8);
    w(20) <= not w(9);
    w(21) <= w(9) or w(19);
    w(22) <= w(0) or w(21);
    w(23) <= w(5);
    w(24) <= w(14) or w(17);
    w(25) <= w(5) or w(8);
    w(26) <= not w(17);
    w(27) <= w(2) or w(13);
    w(28) <= not(w(16) and w(3));
    w(29) <= not(w(4) and w(22));
    w(30) <= not(w(8) or w(1));
    w(31) <= w(10) and w(0);
    w(32) <= w(21);
    w(33) <= not(w(18) or w(2));
    w(34) <= w(3) and w(22);
    w(35) <= w(32) and w(0);
    w(36) <= w(29) and w(18);
    w(37) <= not(w(18) or w(22));
    w(38) <= not(w(8) or w(18));
    w(39) <= not(w(6) or w(4));
    w(40) <= w(15) and w(13);
    w(41) <= not(w(40) or w(34));
    w(42) <= not(w(36) and w(41));
    w(43) <= not w(19);
    w(44) <= w(22) and w(14);
    w(45) <= not w(7);
    w(46) <= not w(28);
    w(47) <= w(0);
    w(48) <= not w(11);
    w(49) <= w(24);
    w(50) <= not(w(32) and w(5));
    w(51) <= not w(36);
    w(52) <= w(10);
    w(53) <= not w(34);
    w(54) <= w(3) xor w(33);
    w(55) <= w(16) or w(34);
    alarm_out <= w(42);
end Behavioral;