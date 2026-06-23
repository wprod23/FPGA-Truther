# Step 1: Parse The Net List
from lib import *
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="Select .vo File", 
    filetypes=[("Verilog Simulation Model File", "*.vo")])

if not file_path:
    print("No File Selected. Closing Program")
    raise SystemExit

print(file_path)

data = read_vo_file(file_path)

comments = data["comments"]
module_name = data["module_name"]
inputs = data["inputs"]
outputs = data["outputs"]
wires = data["wires"]
luts = data["luts"]
ibufs = data["ibufs"]
obufs = data["obufs"]

for comment in comments:
    print(red + comment + clear)

print(green + f"Running Truther For '{module_name.split(" ")[1]}' Module" + clear + "\n")


print(blue + f"Found Inputs For '{module_name.split(" ")[1]}' Module:" + clear)
for input in inputs:
    print(blue + f"  {input}" + clear)

print("\n" + blue + f"Found Outputs For '{module_name.split(" ")[1]}' Module:" + clear)
for output in outputs:
    print(blue + f"  {output}" + clear)

print("-" * 100)

# Step 2: Build Dependency Graph

# Find Dependencies
node_dep = find_dependencies(inputs, outputs, wires, ibufs, obufs, luts)

# Find Consumers
node_con = find_consumers(inputs, outputs, wires, ibufs, obufs, luts)

# Find Dep Count
dep_count = find_dep_count(node_dep)


# Topological Sort
unresolved_counts = dep_count
execution_order = topological_sort(unresolved_counts, node_con)

# EXCECUTION

# Sort Inputs & Outputs

inputs = sort_pins_msb_first(inputs)
outputs = sort_pins_msb_first(outputs)

# Step 3: Lut Logic Evaluator

lut_lookup = generate_lut_lookup(luts)

ibufs_map = {b["in"]: b["out"] for b in ibufs} # Raw Pin -> internal _d wire
obufs_map = {b["in"]: b["out"] for b in obufs} # Internal _d wire -> Raw Pin

# Calculate Column Widths and Add Padding

print("-"*100 + "\n")

print(f"Truth Table For {module_name} Module:")

header_string, divider_string, input_widths, output_widths = generate_headers(inputs, outputs)
print(header_string)
print(divider_string)

# Step 4: Simulate and Generate Truth Table

run_sim(execution_order, inputs, outputs, ibufs_map, obufs_map, lut_lookup, input_widths, output_widths) # Runs Simulation and Prints Truth Table