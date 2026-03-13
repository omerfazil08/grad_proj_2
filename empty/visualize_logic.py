import re
import os
from graphviz import Digraph

# CONFIGURATION: Add your 4 filenames here
VHDL_FILES = [
    "reflex_core_outer_race.vhd",
    "reflex_core_specialized_inner_race.vhd",
    "reflex_core_ball.vhd",
    # "reflex_engine_top.vhd"
]


def parse_vhdl_logic(file_path):
    """
    Parses a VHDL file to extract logic gate connections from CGP code.
    Returns a dictionary of wires and their logic definitions.
    """
    logic_map = {}

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip().lower()
        # Look for assignments.
        # We accept any assignment that has a 'w(' or 'sensor' on the right side
        if "<=" in line:
            # Clean up the line
            line = line.replace(";", "").replace("not(", "not ").replace(")", "")
            parts = line.split("<=")
            target = parts[0].strip()
            expr = parts[1].strip()

            # Skip complex vector assignments like w(15 downto 0)
            if "downto" in target:
                continue

            # Only process if it involves internal wires or sensors
            if "w(" in expr or "sensor" in expr:
                # Extract inputs
                inputs = re.findall(r'w\(\d+\)|sensor_stream\(\d+\)', expr)

                operator = "BUF"  # Default buffer
                if "and" in expr:
                    operator = "AND"
                elif "or" in expr:
                    operator = "OR"
                elif "xor" in expr:
                    operator = "XOR"
                elif "not" in expr:
                    operator = "NOT"

                logic_map[target] = {
                    "op": operator,
                    "inputs": inputs,
                    "expr": expr
                }

    return logic_map


def get_index(w_str):
    """Safe extraction of wire index number."""
    match = re.search(r'\d+', w_str)
    return int(match.group()) if match else -1


def draw_circuit(filename, logic_map):
    """
    Generates a Graphviz diagram for the parsed logic.
    """
    dot = Digraph(comment=filename, format='png')
    dot.attr(rankdir='LR')  # Left-to-Right layout
    dot.attr('node', shape='box', style='filled', fillcolor='lightblue')

    # 1. Identify the 'Output' Node
    # Priority A: Explicit 'alarm_out' signal
    # Priority B: The highest index 'w' wire

    all_wires = list(logic_map.keys())
    if not all_wires:
        print(f"No logic found in {filename}")
        return

    final_wire = None

    if "alarm_out" in logic_map:
        final_wire = "alarm_out"
    else:
        # Fallback: Find highest numbered wire
        w_wires = [w for w in all_wires if "w(" in w]
        if w_wires:
            sorted_wires = sorted(w_wires, key=get_index, reverse=True)
            final_wire = sorted_wires[0]
        else:
            final_wire = all_wires[0]  # Desperate fallback

    # 2. Recursive function to add nodes
    visited = set()

    def add_node(wire_name):
        if wire_name in visited:
            return
        visited.add(wire_name)

        # If it's a sensor input
        if "sensor" in wire_name:
            label = wire_name.replace("sensor_stream", "In")
            dot.node(wire_name, label, shape='circle', fillcolor='#E0E0E0')
            return

        # If it's a logic gate
        if wire_name in logic_map:
            details = logic_map[wire_name]
            op = details['op']

            # Visual styling
            gate_label = f"{op}"

            color = 'white'
            shape = 'invtriangle'
            if op == "AND": color = '#FFCCCC'; shape = 'invtrapezium'
            if op == "OR":  color = '#CCFFCC'; shape = 'invtriangle'
            if op == "XOR": color = '#CCCCFF'; shape = 'diamond'
            if op == "NOT": color = '#FFFFCC'; shape = 'triangle'
            if op == "BUF": color = 'white';   shape = 'ellipse'

            dot.node(wire_name, gate_label, shape=shape, fillcolor=color, style='filled')

            # Connect inputs to this gate
            for inp in details['inputs']:
                add_node(inp)  # Recursively add children
                dot.edge(inp, wire_name)
        else:
            # Wire exists in inputs but not as a target (e.g. raw w(0-15) inputs)
            pass

    # Build graph starting from output
    print(f"Tracing logic for {filename} starting from {final_wire}...")
    add_node(final_wire)

    # Add a final label node
    dot.node("FINAL_OUT", "ALARM", shape='doublecircle', fillcolor='red', style='filled')
    dot.edge(final_wire, "FINAL_OUT")

    # Render
    output_filename = filename.replace(".vhd", "_logic")
    dot.render(output_filename, view=False)
    print(f"Generated: {output_filename}.png")


# Main Execution
for vhdl_file in VHDL_FILES:
    if os.path.exists(vhdl_file):
        print(f"Processing {vhdl_file}...")
        try:
            logic_data = parse_vhdl_logic(vhdl_file)
            draw_circuit(vhdl_file, logic_data)
        except Exception as e:
            print(f"Error processing {vhdl_file}: {e}")
    else:
        print(f"Skipping {vhdl_file} (Not found)")