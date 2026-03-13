library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ball_fault_detector is
    Port ( inputs : in  STD_LOGIC_VECTOR (15 downto 0);
           alarm  : out STD_LOGIC);
end ball_fault_detector;

architecture Behavioral of ball_fault_detector is
    -- Internal signals for the gate outputs
    signal s_16, s_17, s_18, s_19, s_20, s_21, s_22, s_23, s_24, s_25, s_26, s_27, s_28, s_29, s_30, s_31, s_32, s_33, s_34, s_35, s_36, s_37, s_38, s_39, s_40, s_41, s_42, s_43, s_44, s_45 : STD_LOGIC;
begin
    -- Logic Definition
    s_16 <= inputs(5) OR inputs(7);
    s_17 <= inputs(10);
    s_18 <= inputs(11) AND inputs(2);
    s_19 <= inputs(6);
    s_20 <= inputs(10);
    s_21 <= inputs(5) XOR inputs(12);
    s_22 <= inputs(2) XOR inputs(15);
    s_23 <= s_19 OR s_21;
    s_24 <= inputs(15) NAND inputs(0);
    s_25 <= inputs(4) XOR s_24;
    s_26 <= s_23 XOR inputs(13);
    s_27 <= inputs(12) OR s_25;
    s_28 <= inputs(11);
    s_29 <= inputs(4);
    s_30 <= inputs(11) XOR inputs(7);
    s_31 <= inputs(10) OR inputs(4);
    s_32 <= s_27 OR inputs(8);
    s_33 <= s_21 OR s_31;
    s_34 <= inputs(7) AND s_32;
    s_35 <= inputs(7);
    s_36 <= s_16 NAND s_19;
    s_37 <= s_36 AND s_26;
    s_38 <= NOT inputs(13);
    s_39 <= s_22 AND s_38;
    s_40 <= s_20 NOR s_26;
    s_41 <= NOT inputs(11);
    s_42 <= s_33 NAND s_31;
    s_43 <= inputs(10) NOR inputs(8);
    s_44 <= s_43 NOR s_21;
    s_45 <= s_42 OR s_39;

    -- Output Assignment
    alarm <= s_37;

end Behavioral;