# export_vhdl.py
# Run this AFTER main_experiment.py finishes!
from main_experimet import best_global
entity_name = "ball_fault_detector"  # <--- NEW NAME
vhdl_filename = "ball_fault_detector.vhd"

def generate_vhdl(individual, entity_name):
    vhdl = []
    vhdl.append("library IEEE;")
    vhdl.append("use IEEE.STD_LOGIC_1164.ALL;")
    vhdl.append("")
    vhdl.append(f"entity {entity_name} is")
    vhdl.append("    Port ( inputs : in  STD_LOGIC_VECTOR (15 downto 0);")
    vhdl.append("           alarm  : out STD_LOGIC);")
    vhdl.append(f"end {entity_name};")
    vhdl.append("")
    vhdl.append(f"architecture Behavioral of {entity_name} is")
    
    # Declare signals for internal nodes
    vhdl.append("    -- Internal signals for the gate outputs")
    num_inputs = 16
    num_gates = len(individual.nodes)
    
    # Create signals: s_0 to s_15 are inputs, s_16+ are gates
    # We only need to declare signals for gate outputs (s_16 to ...)
    signals = [f"s_{i}" for i in range(num_inputs, num_inputs + num_gates)]
    if signals:
        vhdl.append(f"    signal {', '.join(signals)} : STD_LOGIC;")
    
    vhdl.append("begin")
    vhdl.append("    -- Logic Definition")
    
    gate_names = {0: 'AND', 1: 'OR', 2: 'XOR', 3: 'NAND', 4: 'NOR', 5: 'NOT', 6: 'WIRE'}
    
    for i, node in enumerate(individual.nodes):
        func, in1, in2 = node
        out_idx = num_inputs + i
        
        # Helper to get signal name
        def get_sig(idx):
            if idx < num_inputs: return f"inputs({idx})"
            return f"s_{idx}"
            
        s_out = f"s_{out_idx}"
        s_in1 = get_sig(in1)
        s_in2 = get_sig(in2)
        
        # Write VHDL line
        op = gate_names[func]
        if op == 'WIRE':
            line = f"    {s_out} <= {s_in1};"
        elif op == 'NOT':
            line = f"    {s_out} <= NOT {s_in1};"
        else:
            line = f"    {s_out} <= {s_in1} {op} {s_in2};"
            
        vhdl.append(line)
        
    vhdl.append("")
    vhdl.append("    -- Output Assignment")
    
    # Helper for output
    def get_final_sig(idx):
        if idx < num_inputs: return f"inputs({idx})"
        return f"s_{idx}"
        
    vhdl.append(f"    alarm <= {get_final_sig(individual.output_node)};")
    vhdl.append("")
    vhdl.append("end Behavioral;")
    
    return "\n".join(vhdl)

# Generate and Save
print(f"💾 Generating VHDL for {entity_name}...")
vhdl_code = generate_vhdl(best_global, entity_name)

with open(vhdl_filename, "w") as f:
    f.write(vhdl_code)

print(f"✅ Successfully saved: {vhdl_filename}")
print("   (Download this file to your computer!)")