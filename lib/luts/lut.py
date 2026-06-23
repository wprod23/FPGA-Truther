class LUT:
    def __init__(self, size, dir, inputs, output, truth):
        self.size = size
        self.dir = dir
        self.inputs = inputs
        self.output = output
        self.truth = truth

def evaluate_lut(input_values, init_hex):
    num_inputs = len(input_values)
    total_bits = 2**num_inputs

    init_bin = bin(int(init_hex, 16))[2:].zfill(total_bits) # Convert Hex To Binary String

    index = 0
    for i, val in enumerate(input_values):
        if val == 1:
            index |= (1 << i) # Set Bit To Position 1

    return int(init_bin[-(index+1)])

def generate_lut_lookup(luts):
    lut_lookup = {}

    for lut in luts:
        raw_truth = lut['truth']
        clean_hex = raw_truth.split("'h")[-1] if "'h" in raw_truth else raw_truth
        lut_lookup[lut['output']] = {
            "inputs": lut['inputs'],
            "init": clean_hex
        }

    return lut_lookup