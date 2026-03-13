library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity outer_race_detector is
    Port ( inputs : in  STD_LOGIC_VECTOR (15 downto 0);
           alarm  : out STD_LOGIC);
end outer_race_detector;

architecture Behavioral of outer_race_detector is
    signal s_16, s_17, s_18, s_19, s_20, s_21, s_22, s_23, s_24, s_25, s_26, s_27, s_28, s_29, s_30, s_31, s_32, s_33, s_34, s_35, s_36, s_37, s_38, s_39, s_40, s_41, s_42, s_43, s_44, s_45 : STD_LOGIC;
begin
    s_16 <= inputs(9) OR inputs(14);
    s_17 <= s_16 OR inputs(3);
    s_18 <= inputs(12) XOR inputs(5);
    s_19 <= inputs(2) AND s_17;
    s_20 <= inputs(11) AND inputs(9);
    s_21 <= inputs(0) OR inputs(6);
    s_22 <= inputs(3) XOR inputs(9);
    s_23 <= inputs(6) AND s_17;
    s_24 <= s_22 NOR inputs(1);
    s_25 <= inputs(6) AND s_16;
    s_26 <= inputs(9) NAND inputs(1);
    s_27 <= NOT inputs(4);
    s_28 <= s_18 AND s_17;
    s_29 <= s_25 AND s_23;
    s_30 <= s_18 NAND inputs(5);
    s_31 <= inputs(5) AND inputs(1);
    s_32 <= s_19 AND s_20;
    s_33 <= inputs(9) NAND s_24;
    s_34 <= s_31 XOR s_19;
    s_35 <= s_21 AND s_19;
    s_36 <= NOT inputs(15);
    s_37 <= NOT inputs(5);
    s_38 <= s_29;
    s_39 <= NOT inputs(7);
    s_40 <= s_16;
    s_41 <= inputs(12);
    s_42 <= s_21 OR inputs(14);
    s_43 <= s_28 AND s_42;
    s_44 <= s_39 AND s_35;
    s_45 <= s_34 OR inputs(9);

    alarm <= s_28;
end Behavioral;