-- REFLEX ENGINE: BALL FAULT DETECTOR
-- GENERATED: 2026-01-18 04:22:33.217664
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reflex_core_ball is
    Port ( clk : in STD_LOGIC;
           sensor_stream : in STD_LOGIC_VECTOR(15 downto 0);
           alarm_out : out STD_LOGIC);
end reflex_core_ball;

architecture Behavioral of reflex_core_ball is
    signal w : std_logic_vector(55 downto 0);
begin
    w(15 downto 0) <= sensor_stream;
    w(16) <= w(7) or w(14);
    w(17) <= w(11) xor w(10);
    w(18) <= not(w(10) and w(3));
    w(19) <= not w(17);
    w(20) <= w(3) xor w(18);
    w(21) <= w(5) and w(19);
    w(22) <= w(15) or w(0);
    w(23) <= w(1) xor w(4);
    w(24) <= w(13) or w(5);
    w(25) <= w(10);
    w(26) <= w(4) or w(15);
    w(27) <= w(12) and w(8);
    w(28) <= not(w(14) or w(3));
    w(29) <= w(22) or w(27);
    w(30) <= not(w(26) and w(11));
    w(31) <= not w(19);
    w(32) <= w(28);
    w(33) <= not(w(2) and w(4));
    w(34) <= w(29) and w(22);
    w(35) <= not(w(34) and w(16));
    w(36) <= w(26) xor w(28);
    w(37) <= w(4) and w(4);
    w(38) <= w(9) or w(31);
    w(39) <= not(w(20) or w(31));
    w(40) <= not(w(5) and w(2));
    w(41) <= w(9);
    w(42) <= not w(35);
    w(43) <= w(33) xor w(38);
    w(44) <= not(w(22) or w(28));
    w(45) <= not(w(4) and w(15));
    w(46) <= w(27);
    w(47) <= not(w(8) and w(3));
    w(48) <= w(22);
    w(49) <= not(w(36) or w(43));
    w(50) <= not(w(35) and w(8));
    w(51) <= w(2);
    w(52) <= not(w(20) and w(40));
    w(53) <= w(18) or w(40);
    w(54) <= w(5);
    w(55) <= w(40) or w(13);
    alarm_out <= w(49);
end Behavioral;