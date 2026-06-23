import itertools

file_path = "circuit.vo"

clear_color = "\033[0m"
red_color = "\033[1;31m"

code_data = []
modules = []
inputs = []
outputs = []
wires = []

def defparam_to_truth(def_param):
    hex_val = def_param.split('h')[-1] # Find Hex Characters
    binary = bin(int(hex_val,16))[2:] # Convert Hex to Binary
    form_binary = binary.zfill(len(hex_val) * 4) # Format Binary To Required Length For LUT
    bits = form_binary[::-1] # Flip Binary Number To Evaluate
    num_inputs = len(bits).bit_length() - 1

    #print(f"--- Truth Table for {def_param} ({num_inputs}-Input LUT) ---")

    inputs = []
    outputs = []

    # Generate Rows
    for row_idx, inputs_vals in enumerate(itertools.product([0, 1], repeat=num_inputs)):
        inputs.append(inputs_vals)
        outputs.append(bits[row_idx])

    return [inputs, outputs]

def parse_lut(f):
    data = []
    while (line := f.readline()) != ');\n':
        data.append(line)

    data.append(f.readline())
    return data

def parse_buf(f):
    data = []
    while (line := f.readline()) != ');\n':
        data.append(line)

    return data

with open(file_path, 'r') as f:

    lut_data = []
    current_lut_index = 0

    ibufs = []
    obufs = []

    header_data = []
    for i, line in enumerate(f):
        lut_data.append([[],[],[],[]])
        if line[:2] == "//":
            header_data.append(line[:-1])
        else:
            if line[:-1].split(" ")[0] == "module": # Find Modules (Should Only Be One)
                modules.append(line[:-1].split(" ")[1][:-1])
            if line[:-1].split(" ")[0] == "input": # Find INPUTS
                inputs.append(line[:-1].split(" ")[1][:-1])
            if line[:-1].split(" ")[0] == "output": # Find OUTPUTS
                outputs.append(line[:-1].split(" ")[1][:-1])
            if line[:-1].split(" ")[0] == "wire": # Find WIRES
                if line[:-1].split(" ")[1][0] != "\\":
                    wires.append(line[:-1].split(" ")[1][:-1])
                else:
                    wires.append(line[:-1].split(" ")[1])
            if line[:-1].split(" ")[0][:3] == "LUT":
                print(f"FOUND LUT {line[:-1].split(" ")[0]}, With Heirarchy {line[:-1].split(" ")[1]}")
                lut_type = line[:-1].split(" ")[0]
                lut_location = line[:-1].split(" ")[1]
                lut_inputs = []
                lut_output = []

                data = parse_lut(f)
                num_inputs = int(lut_type[3])-1

                for i in range(0, num_inputs+1):
                    input = data[i]
                    input_pin = input[2:][:-2].split("(")[1][:-1]
                    if input_pin[0] != "\\":
                        lut_inputs.append(input_pin)
                    else:
                        input_pin = input[2:][:-2].split("(")[1][:-2]
                        lut_inputs.append(input_pin)

                lut_output = data[num_inputs+1].split(".")[1].split("(")[1][:-2]

                lut_truth = data[num_inputs+2].split(".")[1].split("=")[1][:-2]

                lut_data[current_lut_index][0] = lut_type, lut_location
                lut_data[current_lut_index][1] = lut_inputs
                lut_data[current_lut_index][2] = lut_output
                lut_data[current_lut_index][3] = lut_truth
                current_lut_index += 1

            if line[:-1].split(" ")[0][:4] == "IBUF":
                ibuf_data = parse_buf(f)
                ibuf_in = ibuf_data[0].split(".")[1].split(",")[0].split("(")[1][:-1]
                ibuf_out = ibuf_data[1].split(".")[1].split(",")[0].split("(")[1][:-2]
                ibufs.append([ibuf_in, ibuf_out])

            if line[:-1].split(" ")[0][:4] == "OBUF":
                obuf_data = parse_buf(f)
                obuf_in = obuf_data[0].split(".")[1].split(",")[0].split("(")[1][:-1]
                obuf_out = obuf_data[1].split(".")[1].split(",")[0].split("(")[1][:-2]
                obufs.append([obuf_in, obuf_out])
    
    remove = [[],[],[],[]] # Remove All Empty Entries

    while remove in lut_data:
        lut_data.remove(remove)

for data in header_data:
    print(red_color + data + clear_color)

values = {}

# Inititalise All Value States

def compute():

    for wire in wires:
        if wire not in values:
            values[wire] = 0

    for outs in outputs:
        values[outs] = 99

    # Set IBuffers to Input Values

    for buf in ibufs:
        input = buf[0]
        output = buf[1]
        values[buf[1]] = values[buf[0]]

    for luts in lut_data:
        lut_inputs = luts[1]
        lut_outputs = luts[2]
        lut_truth = luts[3]

        dat_inputs, dat_outputs = defparam_to_truth(lut_truth)

        evald_inputs = []

        for ins in lut_inputs:
            evald_inputs.append(int(values[ins]))

        #print(evald_inputs)
        format_dat_inputs = []
        for ins in dat_inputs:
            format_dat_inputs.append(list(ins))

        correct_row = None

        for i, ins in enumerate(format_dat_inputs):
            if ins == evald_inputs:
                correct_row = i

        correct_output = dat_outputs[correct_row]

        values[lut_outputs] = int(correct_output)

    for buf in obufs:
        input = buf[0]
        output = buf[1]
        values[buf[1]] = values[buf[0]]

    final_truth = []

    for ins in inputs:
        final_truth.append(values[ins])

    for outs in outputs:
        final_truth.append(values[outs])

    return final_truth

def evaluate_truth():

    num_inputs = len(inputs)

    max_val = (2 ** num_inputs)-1

    test_values = []

    for i in range(0, max_val+1):
        test_values.append(bin(i)[2:].zfill(num_inputs))

    truth = []

    for i in range(0, max_val+1):
        test_value = test_values[i]

        for index, ins in enumerate(inputs):
            values[ins] = test_value[index]
        vals = compute()
        truth.append(vals)

    header_string = ""
    for ins in inputs:
        header_string += ins + " | "
    for i, outs in enumerate(outputs):
        if i != len(outputs) - 1:
            header_string += outs + " | "
        else:
            header_string += outs
    print(header_string)

    for rows in truth:
        string = ""
        for i, cols in enumerate(rows):
            if i != len(rows) - 1:
                string += str(cols) + " | "
            else:
                string += str(cols)
        print(string)

    return rows

evaluate_truth()



# LUT3 \f0/h2/s0_d_s
# 3 Indicated Number Of Inputs In Look Up
