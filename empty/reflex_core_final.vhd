-- REFLEX ENGINE GENERATED: 2026-01-14 04:48:33.346922
-- Run ID: FINAL | Penalty: 10.0
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reflex_core_FINAL is
    Port ( clk : in STD_LOGIC;
           sensor_stream : in STD_LOGIC_VECTOR(15 downto 0);
           alarm_out : out STD_LOGIC);
end reflex_core_FINAL;

architecture Behavioral of reflex_core_FINAL is
    signal w : std_logic_vector(55 downto 0);
begin
    w(15 downto 0) <= sensor_stream;
    w(16) <= w(11) or w(10);
    w(17) <= w(14);
    w(18) <= w(15) or w(4);
    w(19) <= not(w(5) or w(18));
    w(20) <= not(w(14) and w(1));
    w(21) <= not(w(12) or w(16));
    w(22) <= not(w(7) or w(15));
    w(23) <= not(w(16) or w(0));
    w(24) <= not(w(18) and w(1));
    w(25) <= not(w(10) and w(14));
    w(26) <= not(w(17) and w(21));
    w(27) <= not(w(6) or w(25));
    w(28) <= w(27);
    w(29) <= not(w(19) or w(23));
    w(30) <= w(11) xor w(11);
    w(31) <= w(8);
    w(32) <= w(21) xor w(18);
    w(33) <= not(w(8) or w(32));
    w(34) <= w(22);
    w(35) <= not(w(16) or w(26));
    w(36) <= w(0) or w(12);
    w(37) <= w(30) xor w(11);
    w(38) <= w(29);
    w(39) <= not w(9);
    w(40) <= not w(2);
    w(41) <= w(10) xor w(7);
    w(42) <= not w(20);
    w(43) <= w(4) and w(30);
    w(44) <= not w(14);
    w(45) <= w(11) xor w(13);
    w(46) <= not w(26);
    w(47) <= not(w(45) and w(8));
    w(48) <= w(1) and w(10);
    w(49) <= w(13);
    w(50) <= w(14) and w(11);
    w(51) <= not(w(29) or w(33));
    w(52) <= w(26) or w(4);
    w(53) <= not(w(24) and w(34));
    w(54) <= not(w(3) or w(19));
    w(55) <= w(49) and w(22);
    alarm_out <= w(38);
end Behavioral;