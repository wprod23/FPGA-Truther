# defparam \f1/h2/s1_d_s .INIT=8'h96;
import itertools

class LUT:
    def __init__(self, lut_type, lut_location, lut_inputs, lut_output, lut_truth):

        self.type = lut_type
        self.location = lut_location
        self.input_pins = lut_inputs
        self.output_pins = lut_output

        self.inputs, self.outputs = self.defparam_to_truth(lut_truth)

        self.prev_outputs = None
        self.settled = False

        print(self.input_pins, self.output_pins)


    def defparam_to_truth(self, def_param):
        hex_val = def_param.split('h')[-1]
        binary = bin(int(hex_val, 16))[2:]
        form_binary = binary.zfill(len(hex_val) * 4)
        bits = form_binary[::-1]
        num_inputs = len(bits).bit_length() - 1

        inputs = []
        outputs = []

        max_rows = 2 ** num_inputs
        row_idx = 0

        while row_idx < max_rows:
            binary_row = bin(row_idx)[2:].zfill(num_inputs)
            
            temp_list = []
            for character in binary_row:
                temp_list.append(int(character))
            
            temp_list.reverse()
            inputs.append(tuple(temp_list))
            outputs.append(int(bits[row_idx]))
            
            row_idx = row_idx + 1

        return [inputs, outputs]
    
    def check_settled(self):
        if self.prev_outputs == self.prev_outputs:
            return True
        else:
            return False
