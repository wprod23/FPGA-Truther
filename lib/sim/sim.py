import itertools
from lib.luts.lut import *

def run_sim(execution_order, inputs, outputs, ibufs_map, obufs_map, lut_lookup, input_widths, output_widths):

    for combination in itertools.product([0,1], repeat=len(inputs)):
        wire_values = {'GND' : 0, 'VCC': 1} # Set GND and VCC values

        for pin, value in zip(inputs, combination):
            wire_values[pin] = value

        for wire in execution_order:
            if wire in ['GND', 'VCC'] or wire in inputs:
                continue

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

        # Print Truth Table
        in_string = " | ".join(str(wire_values[p]).center(input_widths[p]) for p in inputs)
        out_string = " | ".join(str(wire_values[p]).center(output_widths[p]) for p in outputs)
        print(f"{in_string} || {out_string}")

def run_sim_ui(execution_order, inputs, outputs, ibufs_map, obufs_map, lut_lookup, input_widths, output_widths):
    generated_rows = []

    # Clean the lookup tables keys once before entering the loop to ensure no spacing/backslash mismatches
    cleaned_lut_lookup = {}
    for k, v in lut_lookup.items():
        cleaned_key = k.replace('\\', '').strip()
        cleaned_lut_lookup[cleaned_key] = v

    # Clean the maps as well
    cleaned_ibufs = {k.replace('\\', '').strip(): v.replace('\\', '').strip() for k, v in ibufs_map.items()}
    cleaned_obufs = {k.replace('\\', '').strip(): v.replace('\\', '').strip() for k, v in obufs_map.items()}

    for combination in itertools.product([0,1], repeat=len(inputs)):
        wire_values = {'GND' : 0, 'VCC': 1} 

        # Normalize inputs
        for pin, value in zip(inputs, combination):
            wire_values[pin.replace('\\', '').strip()] = value

        for wire in execution_order:
            wire = wire.replace('\\', '').strip()
            if wire in ['GND', 'VCC'] or wire in inputs:
                continue

            # Process Input Buffers
            for inp_pin, out_wire in cleaned_ibufs.items():
                if wire == out_wire:
                    wire_values[wire] = wire_values.get(inp_pin, 0)
                    break

            # Process LUTs using the cleaned dictionary
            if wire in cleaned_lut_lookup:
                curr_lut_inputs = cleaned_lut_lookup[wire]["inputs"]
                init_hex = cleaned_lut_lookup[wire]["init"]

                # Handle constants like 1'b1 or missing wires
                for inp in curr_lut_inputs:
                    inp_clean = inp.replace('\\', '').strip()
                    if inp_clean not in wire_values:
                        if "1'b1" in inp_clean or "VCC" in inp_clean:
                            wire_values[inp_clean] = 1
                        elif "1'b0" in inp_clean or "GND" in inp_clean:
                            wire_values[inp_clean] = 0
                        elif "'" in inp_clean:
                            val_char = inp_clean.split("'")[-1][1:]
                            wire_values[inp_clean] = int(val_char, 16) if val_char else 0
                        else:
                            wire_values[inp_clean] = 0

                current_input_values = [wire_values.get(inp.replace('\\', '').strip(), 0) for inp in curr_lut_inputs]
                wire_values[wire] = evaluate_lut(current_input_values, init_hex)

        # Drive Output Buffers
        for int_wire, out_pin_check in cleaned_obufs.items():
            if int_wire in wire_values:
                wire_values[out_pin_check] = wire_values[int_wire]

        row_inputs = [str(wire_values.get(p.replace('\\', '').strip(), 0)) for p in inputs]
        row_outputs = [str(wire_values.get(p.replace('\\', '').strip(), 0)) for p in outputs]

        generated_rows.append((row_inputs, row_outputs))

    detected_headers = inputs + ["||"] + outputs
    return detected_headers, generated_rows

def evaluate_single_state(pin_states, execution_order, inputs, outputs, ibufs_map, obufs_map, lut_lookup):
    wire_values = {'GND' : 0, 'VCC': 1}

    cleaned_lut_lookup = {k.replace('\\', '').strip(): v for k, v in lut_lookup.items()}
    cleaned_ibufs = {k.replace('\\', '').strip(): v.replace('\\', '').strip() for k, v in ibufs_map.items()}
    cleaned_obufs = {k.replace('\\', '').strip(): v.replace('\\', '').strip() for k, v in obufs_map.items()}

    for pin in inputs:
        wire_values[pin.replace('\\', '').strip()] = int(pin_states[pin])

    for wire in execution_order:
        wire = wire.replace('\\', '').strip()
        if wire in ['GND', 'VCC'] or wire in inputs:
            continue

        for inp_pin, out_wire in cleaned_ibufs.items():
            if wire == out_wire:
                wire_values[wire] = wire_values.get(inp_pin, 0)
                break

        if wire in cleaned_lut_lookup:
            curr_lut_inputs = cleaned_lut_lookup[wire]["inputs"]
            init_hex = cleaned_lut_lookup[wire]["init"]

            current_input_values = [wire_values.get(inp.replace('\\', '').strip(), 0) for inp in curr_lut_inputs]
            wire_values[wire] = evaluate_lut(current_input_values, init_hex)

    # Link up final outputs
    for int_wire, out_pin_check in cleaned_obufs.items():
        if int_wire in wire_values:
            wire_values[out_pin_check] = wire_values[int_wire]

    return {p.replace('\\', '').strip(): wire_values.get(p.replace('\\', '').strip(), 0) for p in outputs}