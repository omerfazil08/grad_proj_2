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
    s_16 <= inputs(11) OR inputs(13);
    s_17 <= s_16 OR inputs(2);
    s_18 <= inputs(10);
    s_19 <= inputs(6) NAND inputs(3);
    s_20 <= inputs(2) XOR inputs(6);
    s_21 <= NOT inputs(3);
    s_22 <= inputs(12) NAND inputs(12);
    s_23 <= inputs(6);
    s_24 <= inputs(8) OR s_21;
    s_25 <= s_20 OR inputs(9);
    s_26 <= inputs(5);
    s_27 <= s_23;
    s_28 <= s_26 XOR inputs(14);
    s_29 <= s_21 AND s_26;
    s_30 <= inputs(15) NOR inputs(0);
    s_31 <= inputs(2);
    s_32 <= s_22 NOR s_16;
    s_33 <= s_20 XOR inputs(5);
    s_34 <= NOT s_23;
    s_35 <= s_22 AND s_17;
    s_36 <= inputs(13) OR s_33;
    s_37 <= inputs(10) OR s_23;
    s_38 <= inputs(1) NAND inputs(2);
    s_39 <= inputs(10) XOR inputs(13);
    s_40 <= inputs(7) NOR s_17;
    s_41 <= inputs(1) AND inputs(15);
    s_42 <= inputs(7) AND s_20;
    s_43 <= s_26 NOR s_20;
    s_44 <= s_43;
    s_45 <= s_23 XOR inputs(10);

    -- Output Assignment
    alarm <= s_32;

end Behavioral;