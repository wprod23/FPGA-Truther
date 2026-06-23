def generate_headers(inputs, outputs):
    input_widths = {p: max(len(p), 3) for p in inputs}
    output_widths = {p: max(len(p), 3) for p in outputs}

    header_in = " | ".join(p.center(input_widths[p]) for p in inputs)
    header_out = " | ".join(p.center(output_widths[p]) for p in outputs)
    header_string = f"{header_in} || {header_out}"

    divider_len = sum(input_widths.values()) + (len(inputs) - 1) * 3 + 4 + sum(output_widths.values()) + (len(outputs) - 1) * 3
    divider_string = "-" * divider_len

    return header_string, divider_string, input_widths, output_widths