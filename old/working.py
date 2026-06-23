# Step 1: Parse The Net List
import os
from collections import deque
import re

import xml.etree.ElementTree as ET

def clear_console():
    # 'nt' is for Windows, 'posix' is for macOS and Linux
    os.system('cls' if os.name == 'nt' else 'clear')

# Call the function to clear the screen
clear_console()

class LUT:
    def __init__(self, size, dir, inputs, output, truth):
        self.size = size
        self.dir = dir
        self.inputs = inputs
        self.output = output
        self.truth = truth

    def generate_truth_table(self, truth):
        return 0
    



red = "\033[31m"
green = "\033[32m"
blue = "\033[34m"
clear = "\033[0m"

comments = []
module_name = ""
inputs = []
outputs = []
wires = []
luts = []
ibufs = []
obufs = []

# XML Setup
root = ET.Element("data")

with open("circuit.vo", 'r') as f:

    for i, line in enumerate(f):

        # Check For Comments
        if line[0] == "/":
            comments.append(line[:-1])

        # Check For Module Name
        if line.split(" ")[0] == "module":
            module_name = line[:-2]
        
        # Check For Inputs & Outputs
        if line.split(" ")[0] == "input":
            inputs.append(line.split(" ")[1][:-2])
        if line.split(" ")[0] == "output":
            outputs.append(line.split(" ")[1][:-2])

        # Find Wires
        if line.split(" ")[0] == "wire":
            if line[:-1].split(" ")[1][0] != "\\":
                wires.append(line[:-1].split(" ")[1][:-1])
            else:
                wires.append(line[:-1].split(" ")[1])

        # Find IBUF / OBUF
        if line.split(" ")[0][:4] == "IBUF":
            ibuf_data = []

            while (line := f.readline()) != ');\n':
                ibuf_data.append(line)

            #ibuf_data.append(f.readline())

            ibuf_in = ibuf_data[0].split(".")[1].split(",")[0].split("(")[1][:-1]
            ibuf_out = ibuf_data[1].split(".")[1].split(",")[0].split("(")[1][:-2]

            ibuf = {"in": ibuf_in,
                    "out": ibuf_out}

            ibufs.append(ibuf)       

        if line.split(" ")[0][:4] == "OBUF":
            obuf_data = []

            while (line := f.readline()) != ');\n':
                obuf_data.append(line)

            obuf_in = obuf_data[0].split(".")[1].split(",")[0].split("(")[1][:-1]
            obuf_out = obuf_data[1].split(".")[1].split(",")[0].split("(")[1][:-2]

            obuf = {"in": obuf_in,
                    "out": obuf_out}

            obufs.append(obuf)            
     

        # Find LUTS
        if line.split(" ")[0][:3] == "LUT":
            size = line.split(" ")[0][-1]

            lut_dir = line.split(" ")[1]

            lut_inputs = []
            num_inputs = int(size)

            data = []

            while (line := f.readline()) != ');\n':
                data.append(line)

            data.append(f.readline())

            for i in range(0, num_inputs):
                input = data[i]
                input_pin = input[2:][:-2].split("(")[1][:-1]
                if input_pin[0] != "\\":
                    lut_inputs.append(input_pin)
                else:
                    input_pin = input[2:][:-2].split("(")[1][:-2]
                    lut_inputs.append(input_pin)

            lut_output = data[num_inputs].split(".")[1].split("(")[1][:-2].split(" ")[0]

            lut_truth = data[num_inputs+1].split(".")[1].split("=")[1][:-2]

            lut_item = ET.SubElement(root, "lut")
            lut_item.set("id", lut_dir)
            lut_item.set("size", size)
            lut_item.set("inputs", lut_inputs)
            lut_item.set("output", lut_output)
            lut_item.set("truth", lut_truth)

            lut = {"id": lut_dir,
                   "size": size,
                   "inputs": lut_inputs,
                   "output": lut_output,
                   "truth": lut_truth}

            luts.append(lut)

            print(size, lut_inputs, lut_output, lut_truth)

tree = ET.ElementTree(root)

with open("dat.xml", "wb") as file:
    tree.write(file, encoding="utf-8", xml_declaration=True)


# Find Dependencies

node_dep = {}

for ins in inputs:
    node_dep[ins] = []

for outs in outputs:
    node_dep[outs] = []

for wire in wires:
    node_dep[wire] = []

print(node_dep)

for ibuf in ibufs:
    buf_output = ibuf["out"]
    buf_input = ibuf["in"]

    current_depend = node_dep[buf_output]
    if buf_input not in current_depend:
        current_depend.append(buf_input)

    node_dep[buf_output] = current_depend

for obuf in obufs:
    buf_output = obuf["out"]
    buf_input = obuf["in"]

    current_depend = node_dep[buf_output]
    if buf_input not in current_depend:
        current_depend.append(buf_input)

    node_dep[buf_output] = current_depend

for lut in luts:
    lut_output = lut["output"]
    lut_inputs = lut["inputs"]

    current_depend = node_dep[lut_output]
    for ins in lut_inputs:
        if ins not in current_depend:
            current_depend.append(ins)

    node_dep[lut_output] = current_depend

# Find Consumers
node_con = {}

for ins in inputs:
    node_con[ins] = []

for outs in outputs:
    node_con[outs] = []

for wire in wires:
    node_con[wire] = []

print(node_dep)

for ibuf in ibufs:
    buf_output = ibuf["out"]
    buf_input = ibuf["in"]

    current_consumer = node_con[buf_input]
    if buf_output not in current_consumer:
        current_consumer.append(buf_output)

    node_con[buf_input] = current_consumer

for obuf in obufs:
    buf_output = obuf["out"]
    buf_input = obuf["in"]

    current_consumer = node_con[buf_input]
    if buf_output not in current_consumer:
        current_consumer.append(buf_output)

    node_con[buf_input] = current_consumer

for lut in luts:
    lut_output = lut["output"]
    lut_inputs = lut["inputs"]

    for ins in lut_inputs:
        current_consumer = node_con[ins]
        if lut_output not in current_consumer:
            current_consumer.append(lut_output)

        node_con[ins] = current_consumer


clear_console()

#print(node_dep)

#print("--------------------")

#print(node_con)

dep_count = {}

for nodes in node_dep:
    num_dep = len(node_dep[nodes])
    dep_count[nodes] = num_dep

#print(dep_count)

unresolved_counts = dep_count

# Topological Sort
ready_pool = deque([wire for wire, count in unresolved_counts.items() if count == 0])

execution_order = []

while ready_pool:
    current_wire = ready_pool.popleft()
    execution_order.append(current_wire)

    for consumer in node_con.get(current_wire, []):
        unresolved_counts[consumer] -= 1

        if unresolved_counts[consumer] == 0:
            ready_pool.append(consumer)

print(" --- TOPOLOGICAL SORT COMPLETE ---")
print(execution_order)

# EXCECUTION
import itertools

def evaluate_lut(input_values, init_hex):
    num_inputs = len(input_values)
    total_bits = 2**num_inputs

    init_bin = bin(int(init_hex, 16))[2:].zfill(total_bits) # Convert Hex To Binary String

    index = 0
    for i, val in enumerate(input_values):
        if val == 1:
            index |= (1 << i) # Set Bit To Position 1

    return int(init_bin[-(index+1)])

def sort_pins_msb_first(pin_list):
    def sort_key(pin):
        match = re.match(r"([a-zA-Z_]+)(\d*)", pin)
        if match:
            prefix, num_str = match.groups()
            num = int(num_str) if num_str else -1
            return (prefix, -num)
        return (pin, 1)
    return sorted(pin_list, key=sort_key)

inputs = sort_pins_msb_first(inputs)
outputs = sort_pins_msb_first(outputs)

lut_lookup = {}

for lut in luts:
    raw_truth = lut['truth']
    clean_hex = raw_truth.split("'h")[-1] if "'h" in raw_truth else raw_truth
    lut_lookup[lut['output']] = {
        "inputs": lut['inputs'],
        "init": clean_hex
    }

ibufs_map = {b["in"]: b["out"] for b in ibufs} # Raw Pin -> internal _d wire
obufs_map = {b["in"]: b["out"] for b in obufs} # Internal _d wire -> Raw Pin

input_widths = {p: max(len(p), 3) for p in inputs}
output_widths = {p: max(len(p), 3) for p in outputs}

header_in = " | ".join(p.center(input_widths[p]) for p in inputs)
header_out = " | ".join(p.center(output_widths[p]) for p in outputs)
print(f"{header_in} || {header_out}")

divider_len = sum(input_widths.values()) + (len(inputs) - 1) * 3 + 4 + sum(output_widths.values()) + (len(outputs) - 1) * 3
print("-" * divider_len)

# Run Simulation & Generate Truth Table

# Added the missing array to product here just in case!
for combination in itertools.product([0,1], repeat=len(inputs)):
    wire_values = {'GND' : 0, 'VCC': 1}

    # This correctly puts a0, a1, b0, b1, cin into wire_values
    for pin, value in zip(inputs, combination):
        wire_values[pin] = value

    for wire in execution_order:
        if wire in ['GND', 'VCC'] or wire in inputs:
            continue

        # --- ALL OF THIS MUST BE INDENTED INSIDE THE WIRE LOOP ---
        for inp_pin, out_wire in ibufs_map.items():
            if wire == out_wire:
                wire_values[wire] = wire_values[inp_pin]
                break

        if wire in lut_lookup:
            curr_lut_inputs = lut_lookup[wire]["inputs"]
            init_hex = lut_lookup[wire]["init"]

            current_input_values = [wire_values[inp] for inp in curr_lut_inputs]

            wire_values[wire] = evaluate_lut(current_input_values, init_hex)

        if wire in outputs:
            for int_wire, out_pin_check in obufs_map.items():
                if wire == out_pin_check:
                    wire_values[wire] = wire_values[int_wire]
                    break
        # --- END OF THE WIRE LOOP ---

    # This print statement stays outside the wire loop, but inside the combination loop
    in_string = " | ".join(str(wire_values[p]).center(input_widths[p]) for p in inputs)
    out_string = " | ".join(str(wire_values[p]).center(output_widths[p]) for p in outputs)
    print(f"{in_string} || {out_string}")


#clear_console()

'''

for comment in comments:
    print(red + comment + clear + "\n")

print(green + f"Running Truther For '{module_name.split(" ")[1]}' Module" + clear + "\n")


print(blue + f"Found Inputs For '{module_name.split(" ")[1]}' Module:" + clear)
for input in inputs:
    print(blue + f"  {input}" + clear)

print("\n" + blue + f"Found Outputs For '{module_name.split(" ")[1]}' Module:" + clear)
for output in outputs:
    print(blue + f"  {output}" + clear)
'''




# Step 2: Build Dependency Graph

# Step 3: Lut Logic Evaluator

# Step 4: Simulate and Generate Truth Table