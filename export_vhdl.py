# --- CONFIGURATION ---
ENTITY_NAME = "reflex_core"
OUTPUT_FILENAME = "reflex_core.vhd"

# We reuse the gate definitions from the engine to ensure 1:1 mapping
GATE_MAP = {
    0: "{} AND {}",
    1: "{} OR {}",
    2: "{} XOR {}",
    3: "NOT ({} AND {})",
    4: "NOT ({} OR {})",
    5: "NOT {}",      # Unary operator
    6: "{}"          # WIRE (Pass-through)
}

def generate_vhdl(individual, window_size):
    """
    Converts a CGP Individual (Genome) into a VHDL Entity.
    """
    vhdl = []
    
    # 1. Header & Entity Declaration
    vhdl.append("library IEEE;")
    vhdl.append("use IEEE.STD_LOGIC_1164.ALL;")
    vhdl.append("")
    vhdl.append(f"entity {ENTITY_NAME} is")
    vhdl.append("    Port (")
    # Input is the sliding window (std_logic_vector)
    vhdl.append(f"        window_in : in STD_LOGIC_VECTOR ({window_size-1} downto 0);")
    vhdl.append("        alarm_out : out STD_LOGIC")
    vhdl.append("    );")
    vhdl.append(f"end {ENTITY_NAME};")
    vhdl.append("")
    
    # 2. Architecture & Signals
    vhdl.append(f"architecture Behavioral of {ENTITY_NAME} is")
    vhdl.append("")
    # We need internal signals for every gate output
    # Nodes are indexed from window_size to window_size + num_gates
    num_gates = len(individual.nodes)
    total_signals = window_size + num_gates
    
    vhdl.append(f"    -- Internal signals for gate outputs")
    # Example: signal node_16, node_17 ...
    for i in range(num_gates):
        node_idx = window_size + i
        vhdl.append(f"    signal node_{node_idx} : STD_LOGIC;")
    
    vhdl.append("")
    vhdl.append("begin")
    vhdl.append("")
    
    # 3. Logic Implementation
    # We loop through the nodes and write their VHDL equation
    for i, node in enumerate(individual.nodes):
        func, in1, in2 = node
        current_node_idx = window_size + i
        
        # Helper to format input names
        def get_signal_name(idx):
            if idx < window_size:
                return f"window_in({idx})" # Raw Input
            else:
                return f"node_{idx}"       # Previous Gate Output

        sig1 = get_signal_name(in1)
        sig2 = get_signal_name(in2)
        
        # Get the VHDL template for this gate type
        op_template = GATE_MAP[func]
        
        # Format the line
        if func == 5 or func == 6: # Unary ops (NOT, WIRE) use only sig1
            logic_expr = op_template.format(sig1)
        else:
            logic_expr = op_template.format(sig1, sig2)
            
        vhdl.append(f"    node_{current_node_idx} <= {logic_expr};")

    vhdl.append("")
    
    # 4. Connect Final Output
    # The output of the entity is the output of the "output_node" gene
    out_idx = individual.output_node
    if out_idx < window_size:
        final_sig = f"window_in({out_idx})"
    else:
        final_sig = f"node_{out_idx}"
        
    vhdl.append(f"    alarm_out <= {final_sig};")
    vhdl.append("")
    vhdl.append("end Behavioral;")
    
    return "\n".join(vhdl)

# --- EXECUTION ---
# This assumes you still have 'best_global' in memory from the previous step
if 'best_global' in globals():
    print(f"💾 Generating VHDL for circuit with fitness {best_global.fitness:.2f}...")
    vhdl_code = generate_vhdl(best_global, WINDOW_SIZE)
    
    # Save to file
    with open(OUTPUT_FILENAME, "w") as f:
        f.write(vhdl_code)
    
    print(f"✅ VHDL saved to {OUTPUT_FILENAME}")
    print("\n--- PREVIEW ---")
    print(vhdl_code)
    print("---------------")
else:
    print("❌ Error: No 'best_global' circuit found. Please run the evolution step first.")