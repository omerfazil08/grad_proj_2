import re
import os

# CONFIGURATION: Add your 4 filenames here
VHDL_FILES = [
    "reflex_core_outer_race.vhd",
    "reflex_core_specialized_inner_race.vhd",
    "reflex_core_ball.vhd",
]


def parse_vhdl_logic(file_path):
    logic_map = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip().lower()
        # Look for assignments (<=)
        if "<=" in line:
            # 1. Basic cleanup: remove semicolon only
            clean_line = line.replace(";", "")

            # 2. Split into Target and Expression
            parts = clean_line.split("<=")
            if len(parts) != 2: continue

            target = parts[0].strip()
            expr = parts[1].strip()

            # Skip vector definitions (e.g. w(55 downto 0))
            if "downto" in target: continue

            # 3. Extract Inputs using Regex (Looks for w(10) or sensor_stream(5))
            # We look for patterns before we do any more text replacement
            inputs = re.findall(r'w\(\d+\)|sensor_stream\(\d+\)', expr)

            # 4. Determine Operator
            operator = "BUF"
            if "and" in expr:
                operator = "AND"
            elif "or" in expr:
                operator = "OR"
            elif "xor" in expr:
                operator = "XOR"
            elif "not" in expr:
                operator = "NOT"

            # 5. Store in map
            if inputs:
                logic_map[target] = {"op": operator, "inputs": inputs}
            elif target == "alarm_out" and "w(" in expr:
                # Catch the final assignment like: alarm_out <= w(49);
                # The regex might have missed if inputs was empty, retry strict regex
                strict_inputs = re.findall(r'w\(\d+\)', expr)
                if strict_inputs:
                    logic_map[target] = {"op": "BUF", "inputs": strict_inputs}

    return logic_map


def get_index(w_str):
    match = re.search(r'\d+', w_str)
    return int(match.group()) if match else -1


def generate_dot_text(filename, logic_map):
    dot_lines = []
    dot_lines.append(f'digraph "{filename}" {{')
    dot_lines.append('  rankdir="LR";')
    dot_lines.append('  node [shape=box, style=filled, fillcolor=lightblue];')

    all_wires = list(logic_map.keys())
    if not all_wires:
        print(f"DEBUG: No logic found in {filename}")
        return

    # Find the start node (alarm_out)
    final_wire = None
    if "alarm_out" in logic_map:
        final_wire = "alarm_out"
    else:
        # Fallback to highest index wire
        w_wires = [w for w in all_wires if "w(" in w]
        if w_wires:
            final_wire = sorted(w_wires, key=get_index, reverse=True)[0]
        else:
            final_wire = all_wires[0]

    visited = set()

    def add_node(wire_name):
        if wire_name in visited: return
        visited.add(wire_name)

        # Draw Sensor Inputs
        if "sensor" in wire_name:
            label = wire_name.replace("sensor_stream", "In")
            clean_label = re.sub(r'[()]', '', label)  # Remove parens for cleaner label
            dot_lines.append(f'  "{wire_name}" [label="{clean_label}", shape=circle, fillcolor="#E0E0E0"];')
            return

        # Draw Logic Gates
        if wire_name in logic_map:
            details = logic_map[wire_name]
            op = details['op']

            # Styling
            color = 'white';
            shape = 'invtriangle'
            if op == "AND": color = '#FFCCCC'; shape = 'invtrapezium'
            if op == "OR":  color = '#CCFFCC'; shape = 'invtriangle'
            if op == "XOR": color = '#CCCCFF'; shape = 'diamond'
            if op == "NOT": color = '#FFFFCC'; shape = 'triangle'
            if op == "BUF": color = 'white';   shape = 'ellipse'

            # Draw the node
            # Use wire_name as ID, but Op as Label
            dot_lines.append(f'  "{wire_name}" [label="{op}", shape={shape}, fillcolor="{color}"];')

            # Draw edges from inputs to this node
            for inp in details['inputs']:
                add_node(inp)
                dot_lines.append(f'  "{inp}" -> "{wire_name}";')

    print(f"Tracing logic for {filename} starting from {final_wire}...")
    add_node(final_wire)

    # Final Output Connection
    dot_lines.append(f'  "{final_wire}" -> "ALARM";')
    dot_lines.append('  "ALARM" [shape=doublecircle, fillcolor=red];')
    dot_lines.append('}')

    print(f"\n--- COPY BELOW THIS LINE FOR {filename} ---")
    print("\n".join(dot_lines))
    print(f"--- END OF CODE FOR {filename} ---\n")


# Main Execution
for vhdl_file in VHDL_FILES:
    if os.path.exists(vhdl_file):
        try:
            logic_data = parse_vhdl_logic(vhdl_file)
            generate_dot_text(vhdl_file, logic_data)
        except Exception as e:
            print(f"Error processing {vhdl_file}: {e}")
    else:
        print(f"Skipping {vhdl_file} (Not found)")