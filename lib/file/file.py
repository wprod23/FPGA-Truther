import re
import tkinter as tk
from tkinter import filedialog

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select .vo File", 
        filetypes=[("Verilog Simulation Model File", "*.vo")])

    if not file_path:
        print("No File Selected. Closing Program")
        raise SystemExit
    
    return file_path

def read_vo_file(file):
    comments = []
    module_name = ""
    inputs = []
    outputs = []
    wires = []
    luts = []
    ibufs = []
    obufs = []

    with open(file, 'r') as f:

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

                lut = {"id": lut_dir,
                    "size": size,
                    "inputs": lut_inputs,
                    "output": lut_output,
                    "truth": lut_truth}

                luts.append(lut)


    comments.append(f"Running Truther For '{module_name.split(" ")[1]}' Module")
    comments.append(f"Found Inputs For '{module_name.split(" ")[1]}' Module:")
    for input in inputs:
        comments.append(f"  {input}")

    comments.append(f"Found Outputs For '{module_name.split(" ")[1]}' Module:")
    for output in outputs:
        comments.append(f"  {output}")

    data = {
        "comments": comments,
        "module_name": module_name,
        "inputs": inputs,
        "outputs": outputs,
        "wires": wires,
        "luts": luts,
        "ibufs": ibufs,
        "obufs": obufs
    }

    return data

def read_vo_file_regex(file):
    comments = []
    module_name = ""
    inputs = []
    outputs = []
    wires = []
    luts = []
    ibufs = []
    obufs = []

    # Read the file using standard string translation, but instantly fix form-feed errors
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert form-feed character escapes back into physical characters
    content = content.replace('\f', 'f').replace('\t', ' ')

    # Core single-line declarations
    comment_pat = re.compile(r'^//\s*(.*)')
    module_pat  = re.compile(r'^module\s+(\w+)')
    input_pat   = re.compile(r'^input\s+\\?([\w\[\]\.\/\-_]+)\s*;')
    output_pat  = re.compile(r'^output\s+\\?([\w\[\]\.\/\-_]+)\s*;')
    wire_pat    = re.compile(r'^wire\s+\\?([\w\[\]\.\/\-_]+)\s*;')

    # Process metadata line by line
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if m := comment_pat.match(line):
            comments.append(m.group(1))
            continue
        if m := module_pat.match(line):
            module_name = f"module {m.group(1)};"
            continue
        
        # Strip backslashes on declarations to align dictionary keys
        if m := input_pat.match(line):
            inputs.append(m.group(1).replace('\\', '').strip())
            continue
        if m := output_pat.match(line):
            outputs.append(m.group(1).replace('\\', '').strip())
            continue
        if m := wire_pat.match(line):
            wires.append(m.group(1).replace('\\', '').strip())
            continue

    # 1. Parse Input Buffers (IBUFs) safely without bracket clipping
    for block in re.finditer(r'IBUF\s+[\s\S]*?;\s*', content):
        block_text = block.group(0)
        ports = re.findall(r'\.(\w+)\s*\(\s*([^\)]+?)\s*\)', block_text)
        pins = {port.strip(): wire.replace('\\', '').strip() for port, wire in ports}
        if 'I' in pins and 'O' in pins:
            ibufs.append({"in": pins['I'], "out": pins['O']})

    # 2. Parse Output Buffers (OBUFs) safely without bracket clipping
    for block in re.finditer(r'OBUF\s+[\s\S]*?;\s*', content):
        block_text = block.group(0)
        ports = re.findall(r'\.(\w+)\s*\(\s*([^\)]+?)\s*\)', block_text)
        pins = {port.strip(): wire.replace('\\', '').strip() for port, wire in ports}
        if 'I' in pins and 'O' in pins:
            obufs.append({"in": pins['I'], "out": pins['O']})

    # 3. Parse LUTs safely without bracket clipping
    for block in re.finditer(r'LUT(\d)\s+([^\(]+)\s*\(([\s\S]*?)\)\s*;\s*', content):
        lut_size = block.group(1)
        raw_id = block.group(2).strip()
        lut_id = raw_id.replace('\\', '').strip()
        block_body = block.group(3)

        # Non-greedy inner capture safely scoops up brackets, slashes, and dots
        raw_pins = re.findall(r'\.(\w+)\s*\(\s*([^\)]+?)\s*\)', block_body)
        
        # Sort tracking the string representation of the port key cleanly
        raw_pins_sorted = sorted(raw_pins, key=lambda x: str(x).lower())
        pins = [(port.strip(), wire.replace('\\', '').strip()) for port, wire in raw_pins_sorted]
        
        lut_inputs = [wire for port, wire in pins if port.startswith('I') or port.startswith('data')]
        lut_output = next((wire for port, wire in pins if port in ('F', 'combout', 'O', 'o')), "")
       
        # Isolate core gate name without hierarchy to avoid slash traps
        core_id = lut_id.split('/')[-1] 
        
        # Look for the defparam matching this core name
        mask_match = re.search(fr'defparam[\s\S]*?{re.escape(core_id)}[\s\S]*?\.(?:INIT|lut_mask)\s*=\s*[^;]*?\'h([0-9A-Fa-f]+)', content)
        lut_truth = mask_match.group(1) if mask_match else "0"

        luts.append({
            "id": lut_id,
            "size": lut_size,
            "inputs": lut_inputs,  
            "output": lut_output,  
            "truth": lut_truth
        })

    # Format user logs using the second word index to grab the clean name
    clean_name = module_name.split(" ")[0].replace(";", "") if " " in module_name else "Unknown"
    comments.append(f"Running Truther For '{clean_name}' Module")
    comments.append(f"Found Inputs For '{clean_name}' Module:")
    comments.extend(f"  {inp}" for inp in inputs)
    comments.append(f"Found Outputs For '{clean_name}' Module:")
    comments.extend(f"  {out}" for out in outputs)

    return {
        "comments": comments,
        "module_name": module_name,
        "inputs": inputs,
        "outputs": outputs,
        "wires": wires,
        "luts": luts,
        "ibufs": ibufs,
        "obufs": obufs
    }