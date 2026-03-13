library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity reflex_engine_top is
    Port (
        clk           : in  STD_LOGIC;
        rst           : in  STD_LOGIC;
        sensor_stream : in  STD_LOGIC_VECTOR (15 downto 0);

        -- Individual Diagnostics (Which fault is it?)
        led_outer     : out STD_LOGIC;
        led_inner     : out STD_LOGIC;
        led_ball      : out STD_LOGIC;

        -- The Safety Interlock (Stop the machine!)
        motor_shutdown : out STD_LOGIC
    );
end reflex_engine_top;

architecture Behavioral of reflex_engine_top is

    -- 1. Signals for the Raw Reflex Outputs
    signal raw_outer_trip : std_logic;
    signal raw_inner_trip : std_logic;
    signal raw_ball_trip  : std_logic;

    -- 2. Combined Raw Trip
    signal any_fault_detected : std_logic;

    -- 3. Persistence Counter (The "Council Defense" Logic)
    -- We require 5 detections in a row (or short window) to trigger shutdown.
    signal persistence_counter : unsigned(3 downto 0) := (others => '0');
    constant TRIP_THRESHOLD    : unsigned(3 downto 0) := "0101"; -- 5 Counts

begin

    -- =========================================================================
    -- INSTANTIATE THE CHAMPIONS
    -- =========================================================================

    -- Champion 1: Outer Race (From Sweep Run)
    CORE_OUTER: entity work.reflex_core_outer_race
    port map (
        clk => clk,
        sensor_stream => sensor_stream,
        alarm_out => raw_outer_trip
    );

    -- Champion 2: Inner Race (From Specialist Island Run)
    CORE_INNER: entity work.reflex_core_specialized_inner_race
    port map (
        clk => clk,
        sensor_stream => sensor_stream,
        alarm_out => raw_inner_trip
    );

    -- Champion 3: Ball Fault (From Specialist Island Run)
    CORE_BALL: entity work.reflex_core_specialized_ball
    port map (
        clk => clk,
        sensor_stream => sensor_stream,
        alarm_out => raw_ball_trip
    );

    -- =========================================================================
    -- DIAGNOSTIC OUTPUTS (Instant Feedback)
    -- =========================================================================
    led_outer <= raw_outer_trip;
    led_inner <= raw_inner_trip;
    led_ball  <= raw_ball_trip;

    -- =========================================================================
    -- SAFETY INTERLOCK LOGIC (Persistence Filter)
    -- =========================================================================
    any_fault_detected <= raw_outer_trip or raw_inner_trip or raw_ball_trip;

    process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                persistence_counter <= (others => '0');
                motor_shutdown <= '0';
            else
                -- If ANY core is screaming, increment counter
                if any_fault_detected = '1' then
                    if persistence_counter < TRIP_THRESHOLD then
                        persistence_counter <= persistence_counter + 1;
                    end if;
                else
                    -- If silence, decay the counter (Integrator Leak)
                    if persistence_counter > 0 then
                        persistence_counter <= persistence_counter - 1;
                    end if;
                end if;

                -- Latch the Shutdown if Threshold Met
                if persistence_counter >= TRIP_THRESHOLD then
                    motor_shutdown <= '1';
                else
                    motor_shutdown <= '0';
                end if;
            end if;
        end if;
    end process;

end Behavioral;