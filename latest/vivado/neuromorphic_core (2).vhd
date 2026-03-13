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

    -- 1. Declare Inner Race (Reflex A)
    -- Note: Uses its original port names (window_in, alarm_out)
    component reflex_core is
        Port ( window_in : in  STD_LOGIC_VECTOR (15 downto 0);
               alarm_out : out STD_LOGIC);
    end component;

    -- 2. Declare Ball Fault (Reflex B)
    component ball_fault_detector is
        Port ( inputs : in  STD_LOGIC_VECTOR (15 downto 0);
               alarm  : out STD_LOGIC);
    end component;

    -- 3. Declare Outer Race (Reflex C)
    component outer_race_detector is
        Port ( inputs : in  STD_LOGIC_VECTOR (15 downto 0);
               alarm  : out STD_LOGIC);
    end component;

    -- Internal signals to catch the individual screams
    signal alarm_inner : STD_LOGIC;
    signal alarm_ball  : STD_LOGIC;
    signal alarm_outer : STD_LOGIC;

begin

    -- Instantiate Reflex A (Inner Race)
    Unit_Inner: reflex_core
    port map (
        window_in => sensor_data,
        alarm_out => alarm_inner
    );

    -- Instantiate Reflex B (Ball Fault)
    Unit_Ball: ball_fault_detector
    port map (
        inputs => sensor_data,
        alarm  => alarm_ball
    );

    -- Instantiate Reflex C (Outer Race)
    Unit_Outer: outer_race_detector
    port map (
        inputs => sensor_data,
        alarm  => alarm_outer
    );

    -- The "3-Way OR" Logic
    -- If ANY detector sees a fault, pull the Master Alarm.
    master_alarm <= alarm_inner OR alarm_ball OR alarm_outer;

end Structural;