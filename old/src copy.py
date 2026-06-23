
import lut

file_path = "circuit.vo"

clear_color = "\033[0m"
red_color = "\033[1;31m"
green_color = "\033[1;32m"
blue_color = "\033[1;34m"

class Truther:
    def __init__(self, file_path):
        self.modules = []
        self.inputs = []
        self.outputs = []
        self.wires = []
        self.header_data = []
        self.lut_data = []
        self.file_path = file_path

    def parse_lut(self, f):
        data = []
        while (line := f.readline()) != ');\n':
            data.append(line)

        data.append(f.readline())
        return data

    def parse_buf(self, f):
        data = []
        while (line := f.readline()) != ');\n':
            data.append(line)

        return data
    
    def read_data(self):
        with open(self.file_path, 'r') as f:

            current_lut_index = 0

            self.ibufs = []
            self.obufs = []

            for i, line in enumerate(f):
                self.lut_data.append([[],[],[],[]])
                if line[:2] == "//":
                    self.header_data.append(line[:-1])
                else:
                    if line[:-1].split(" ")[0] == "module": # Find Modules (Should Only Be One)
                        self.modules.append(line[:-1].split(" ")[1][:-1])
                    if line[:-1].split(" ")[0] == "input": # Find INPUTS
                        self.inputs.append(line[:-1].split(" ")[1][:-1])
                    if line[:-1].split(" ")[0] == "output": # Find OUTPUTS
                        self.outputs.append(line[:-1].split(" ")[1][:-1])
                    if line[:-1].split(" ")[0] == "wire": # Find WIRES
                        if line[:-1].split(" ")[1][0] != "\\":
                            self.wires.append(line[:-1].split(" ")[1][:-1])
                        else:
                            self.wires.append(line[:-1].split(" ")[1])
                    if line[:-1].split(" ")[0][:3] == "LUT":
                        #print(f"FOUND LUT {line[:-1].split(" ")[0]}, With Heirarchy {line[:-1].split(" ")[1]}")
                        lut_type = line[:-1].split(" ")[0]
                        lut_location = line[:-1].split(" ")[1]
                        lut_inputs = []
                        lut_output = []

                        data = self.parse_lut(f)
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

                        '''
                        self.lut_data[current_lut_index][0] = lut_type, lut_location
                        self.lut_data[current_lut_index][1] = lut_inputs
                        self.lut_data[current_lut_index][2] = lut_output
                        self.lut_data[current_lut_index][3] = lut_truth
                        '''

                        print(lut_truth)

                        lut_1 = lut.LUT(lut_type, lut_location, lut_inputs, lut_output, lut_truth)

                        self.lut_data[current_lut_index] = lut_1

                        current_lut_index += 1

                    if line[:-1].split(" ")[0][:4] == "IBUF":
                        ibuf_data = self.parse_buf(f)
                        ibuf_in = ibuf_data[0].split(".")[1].split(",")[0].split("(")[1][:-1]
                        ibuf_out = ibuf_data[1].split(".")[1].split(",")[0].split("(")[1][:-2]
                        self.ibufs.append([ibuf_in, ibuf_out])

                    if line[:-1].split(" ")[0][:4] == "OBUF":
                        obuf_data = self.parse_buf(f)
                        obuf_in = obuf_data[0].split(".")[1].split(",")[0].split("(")[1][:-1]
                        obuf_out = obuf_data[1].split(".")[1].split(",")[0].split("(")[1][:-2]
                        self.obufs.append([obuf_in, obuf_out])
            
            remove = [[],[],[],[]] # Remove All Empty Entries

            while remove in self.lut_data:
                self.lut_data.remove(remove)

    def compute(self):
        #print(green_color + "Generating Wire and Output Base Values" + clear_color)

        for outs in self.outputs:
            self.values[outs] = 99

        # Set IBuffers to Input Values

        #print(blue_color + "Setting Input Buffers To Input Values" + clear_color)

        for buf in self.ibufs:
            self.values[buf[1]] = self.values[buf[0]]

        no_settled = 0
        trials = 0

        while trials < 5 or no_settled != len(self.lut_data):
            no_settled = 0
            for luts in self.lut_data:
                lut_inputs = luts.input_pins
                lut_outputs = luts.output_pins

                #print(green_color + f"Generating Truth Table For {luts[0][0]} {luts[3]}" + clear_color)

                dat_inputs, dat_outputs = luts.inputs, luts.outputs

                evald_inputs = []

                for ins in lut_inputs:
                    evald_inputs.append(int(self.values[ins]))

                format_dat_inputs = []
                for ins in dat_inputs:
                    format_dat_inputs.append(list(ins))

                correct_row = None

                #print(blue_color + f"Finding Output For {evald_inputs}" + clear_color)

                for i, ins in enumerate(format_dat_inputs):
                    if ins == evald_inputs:
                        correct_row = i

                correct_output = dat_outputs[correct_row]

                self.values[lut_outputs] = int(correct_output)

                if luts.check_settled():
                    no_settled += 1

                luts.prev_outputs = correct_output

            trials += 1
            print(trials)


        #print(blue_color + f"Setting Output Values To Output Buffer Values" + clear_color)

        for buf in self.obufs:
            self.values[buf[1]] = self.values[buf[0]]

        final_truth = []

        for ins in self.inputs:
            final_truth.append(self.values[ins])
        
        #print(final_truth)

        for outs in self.outputs:
            final_truth.append(self.values[outs])

        #print(final_truth)

        return final_truth
    
    def evaluate_truth(self):

        #print(green_color + "Generating Test Values" + clear_color)

        num_inputs = len(self.inputs)

        max_val = (2 ** num_inputs)-1

        test_values = []

        for i in range(0, max_val+1):
            test_values.append(bin(i)[2:].zfill(num_inputs))

        #print(test_values)

        truth = []

        for i in range(0, max_val+1):
            test_value = test_values[i]

            for wire in self.wires:
                self.values[wire] = 0

            for index, ins in enumerate(self.inputs):
                self.values[ins] = int(test_value[index])
                
            vals = self.compute()
            truth.append(vals)

        #print(green_color + f"Rendering Truth Table For {self.modules[0]}" + clear_color)
        #print(f"\n{self.modules[0]} Truth Table")

        header_string = ""
        for ins in self.inputs:
            header_string += ins + " | "
        for i, outs in enumerate(self.outputs):
            if i != len(self.outputs) - 1:
                header_string += outs + " | "
            else:
                header_string += outs
        print(header_string)

        for rows in truth:
            string = ""
            for i, cols in enumerate(rows):
                if i == len(self.inputs)-1:
                    string += str(cols) + " : "
                elif i != len(rows) - 1:
                    string += str(cols) + " | "
                else:
                    string += str(cols)
            print(string) ## PRINT LINE ------------------------------------------------ *

        return rows


    def run(self):
        self.read_data()

        for data in self.header_data:
            print(red_color + data + clear_color)

        self.values = {}

        # Sort Inputs and Outputs
        def input_sort_key(var_name):
            import re
            match = re.match(r"([a-zA-Z]+)(\d*)", var_name)
            if match:
                base, index = match.groups()

                priority = 0 if base.lower() in ['a', 'b', 'x', 'y'] else 1
                num = int(index) if index else -1
                return (priority, base, -num)
            return (2, var_name, 0)
        
        def output_sort_key(var_name):
            import re
            if 'cout' in var_name.lower():
                return (0, "")
            match = re.match(r"([a-zA-Z]+)(\d*)", var_name)
            if match:
                base, index = match.groups()
                num = int(index) if index else -1
                return (1, base, -num)
            return (2, var_name, 0)
        
        self.inputs = sorted(self.inputs, key=input_sort_key)
        self.outputs = sorted(self.outputs, key=output_sort_key)

        self.evaluate_truth()


# Inititalise All Value States

new_truth = Truther("circuit.vo")
new_truth.run()

#print(new_truth.lut_data)


# LUT3 \f0/h2/s0_d_s
# 3 Indicated Number Of Inputs In Look Up
