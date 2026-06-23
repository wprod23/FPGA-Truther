import itertools

def get_truth_table(init_str):
    # 1. Isolate the hex characters (e.g., "8'h96" -> "96")
    hex_val = init_str.split('h')[-1]
    
    # 2. Convert to binary and pad it perfectly (4 bits per hex character)
    # [::-1] instantly reverses it so index 0 = Bit 0, index 1 = Bit 1, etc.
    bits = bin(int(hex_val, 16))[2:].zfill(len(hex_val) * 4)[::-1]
    
    # 3. Figure out how many inputs based on the bit count
    num_inputs = len(bits).bit_length() - 1
    
    print(f"--- Truth Table for {init_str} ({num_inputs}-Input LUT) ---")
    
    # 4. Generate rows dynamically using standard counting order
    for row_idx, inputs in enumerate(itertools.product([0, 1], repeat=num_inputs)):
        # inputs is a tuple like (0, 0, 0). We reverse it to print MSB to LSB.
        print(f"Inputs {inputs[::-1]} -> Output: {bits[row_idx]}")

# --- Test it instantly ---
get_truth_table("4'h8")