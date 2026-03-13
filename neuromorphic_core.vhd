library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity neuromorphic_core is
    Port ( 
           -- The single "Microphone" (Sensor Input)
           sensor_data : in  STD_LOGIC_VECTOR (15 downto 0);
           
           -- The Combined Output
           master_alarm : out STD_LOGIC
           );
end neuromorphic_core;

architecture Structural of neuromorphic_core is

    -- 1. Declare the "Inner Race" Component (Reflex #1)
    component reflex_core is
        Port ( inputs : in  STD_LOGIC_VECTOR (15 downto 0);
               alarm  : out STD_LOGIC);
    end component;

    -- 2. Declare the "Ball Fault" Component (Reflex #2)
    component ball_fault_detector is
        Port ( inputs : in  STD_LOGIC_VECTOR (15 downto 0);
               alarm  : out STD_LOGIC);
    end component;

    -- Internal signals to catch the individual screams
    signal alarm_inner_race : STD_LOGIC;
    signal alarm_ball_fault : STD_LOGIC;

begin

    -- 3. Instantiate Reflex #1 (Connect it to sensor)
    Unit_Inner: reflex_core
    port map (
        inputs => sensor_data,
        alarm  => alarm_inner_race
    );

    -- 4. Instantiate Reflex #2 (Connect it to SAME sensor)
    Unit_Ball: ball_fault_detector
    port map (
        inputs => sensor_data,
        alarm  => alarm_ball_fault
    );

    -- 5. The "OR" Logic (If ANYONE screams, pull the lever)
    master_alarm <= alarm_inner_race OR alarm_ball_fault;

end Structural;