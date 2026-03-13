-- SPECIALIZED REFLEX ENGINE: INNER_RACE
-- PENALTY: 4.0 | GENERATIONS: 1200
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reflex_core_specialized_inner_race is
    Port ( clk : in STD_LOGIC; sensor_stream : in STD_LOGIC_VECTOR(15 downto 0); alarm_out : out STD_LOGIC);
end reflex_core_specialized_inner_race;

architecture Behavioral of reflex_core_specialized_inner_race is
    signal w : std_logic_vector(55 downto 0);
begin
    w(15 downto 0) <= sensor_stream;
    w(16) <= w(7) nor w(6);
    w(17) <= w(10) or w(15);
    w(18) <= not w(0);
    w(19) <= w(17) or w(2);
    w(20) <= w(0) and w(10);
    w(21) <= w(7) and w(11);
    w(22) <= w(21) nor w(5);
    w(23) <= w(17);
    w(24) <= w(23) xor w(9);
    w(25) <= w(19) nor w(9);
    w(26) <= w(11) or w(9);
    w(27) <= w(5) or w(7);
    w(28) <= w(10);
    w(29) <= w(13);
    w(30) <= w(12) or w(14);
    w(31) <= w(25) nor w(16);
    w(32) <= w(10);
    w(33) <= w(1) nor w(7);
    w(34) <= w(5);
    w(35) <= w(8) nand w(20);
    w(36) <= not w(34);
    w(37) <= w(0) xor w(16);
    w(38) <= w(25) and w(1);
    w(39) <= w(31) xor w(37);
    w(40) <= w(2) nor w(8);
    w(41) <= w(0) or w(37);
    w(42) <= w(9) xor w(13);
    w(43) <= w(22) nor w(2);
    w(44) <= w(14) and w(20);
    w(45) <= w(22) and w(20);
    w(46) <= w(34) nand w(0);
    w(47) <= w(14);
    w(48) <= not w(36);
    w(49) <= not w(39);
    w(50) <= w(11) nand w(39);
    w(51) <= w(37) xor w(14);
    w(52) <= w(9) nand w(19);
    w(53) <= w(18);
    w(54) <= w(46) xor w(39);
    w(55) <= w(10) nand w(7);
    alarm_out <= w(31);
end Behavioral;