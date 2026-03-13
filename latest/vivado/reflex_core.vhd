library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity reflex_core is
    Port (
        window_in : in STD_LOGIC_VECTOR (15 downto 0);
        alarm_out : out STD_LOGIC
    );
end reflex_core;

architecture Behavioral of reflex_core is

    -- Internal signals for gate outputs
    signal node_16 : STD_LOGIC;
    signal node_17 : STD_LOGIC;
    signal node_18 : STD_LOGIC;
    signal node_19 : STD_LOGIC;
    signal node_20 : STD_LOGIC;
    signal node_21 : STD_LOGIC;
    signal node_22 : STD_LOGIC;
    signal node_23 : STD_LOGIC;
    signal node_24 : STD_LOGIC;
    signal node_25 : STD_LOGIC;
    signal node_26 : STD_LOGIC;
    signal node_27 : STD_LOGIC;
    signal node_28 : STD_LOGIC;
    signal node_29 : STD_LOGIC;
    signal node_30 : STD_LOGIC;
    signal node_31 : STD_LOGIC;
    signal node_32 : STD_LOGIC;
    signal node_33 : STD_LOGIC;
    signal node_34 : STD_LOGIC;
    signal node_35 : STD_LOGIC;
    signal node_36 : STD_LOGIC;
    signal node_37 : STD_LOGIC;
    signal node_38 : STD_LOGIC;
    signal node_39 : STD_LOGIC;
    signal node_40 : STD_LOGIC;
    signal node_41 : STD_LOGIC;
    signal node_42 : STD_LOGIC;
    signal node_43 : STD_LOGIC;
    signal node_44 : STD_LOGIC;
    signal node_45 : STD_LOGIC;

begin

    node_16 <= window_in(4) OR window_in(10);
    node_17 <= NOT window_in(7);
    node_18 <= node_17;
    node_19 <= node_16 AND window_in(8);
    node_20 <= NOT (node_19 OR window_in(0));
    node_21 <= window_in(15) XOR window_in(14);
    node_22 <= NOT window_in(4);
    node_23 <= window_in(5) XOR node_18;
    node_24 <= window_in(15) OR node_23;
    node_25 <= NOT (node_19 OR window_in(0));
    node_26 <= NOT (window_in(14) AND node_25);
    node_27 <= window_in(0) AND node_22;
    node_28 <= window_in(13) XOR window_in(6);
    node_29 <= node_24;
    node_30 <= node_18 AND window_in(11);
    node_31 <= NOT (node_18 AND node_23);
    node_32 <= node_26 XOR window_in(11);
    node_33 <= NOT window_in(10);
    node_34 <= NOT (node_16 OR node_33);
    node_35 <= NOT (node_24 AND node_20);
    node_36 <= NOT (window_in(9) OR node_35);
    node_37 <= NOT node_19;
    node_38 <= node_21 AND window_in(14);
    node_39 <= NOT (window_in(13) OR node_20);
    node_40 <= NOT (node_23 AND node_28);
    node_41 <= node_33 OR node_22;
    node_42 <= NOT node_16;
    node_43 <= NOT (node_26 OR node_17);
    node_44 <= NOT (window_in(13) OR node_25);
    node_45 <= window_in(0) OR node_23;

    alarm_out <= node_19;

end Behavioral;