def find_dependencies(inputs, outputs, wires, ibufs, obufs, luts):

    node_dep = {}

    for ins in inputs:
        node_dep[ins] = []

    for outs in outputs:
        node_dep[outs] = []

    for wire in wires:
        node_dep[wire] = []

    for ibuf in ibufs:
        buf_output = ibuf["out"]
        buf_input = ibuf["in"]

        if buf_output not in node_dep:
            node_dep[buf_output] = []

        current_depend = node_dep[buf_output]
        if buf_input not in current_depend:
            current_depend.append(buf_input)

        node_dep[buf_output] = current_depend

    for obuf in obufs:
        buf_output = obuf["out"]
        buf_input = obuf["in"]

        if buf_output not in node_dep:
            node_dep[buf_output] = []

        current_depend = node_dep[buf_output]
        if buf_input not in current_depend:
            current_depend.append(buf_input)

        node_dep[buf_output] = current_depend

    for lut in luts:
        lut_output = lut["output"]
        lut_inputs = lut["inputs"]

        if lut_output not in node_dep:
            node_dep[lut_output] = []

        current_depend = node_dep[lut_output]
        for ins in lut_inputs:
            if ins not in current_depend:
                current_depend.append(ins)

        node_dep[lut_output] = current_depend

    return(node_dep)

def find_dep_count(node_dep):
    dep_count = {}

    for nodes in node_dep:
        num_dep = len(node_dep[nodes])
        dep_count[nodes] = num_dep

    return dep_count

def find_consumers(inputs, outputs, wires, ibufs, obufs, luts):

    node_con = {}

    for ins in inputs:
        node_con[ins] = []

    for outs in outputs:
        node_con[outs] = []

    for wire in wires:
        node_con[wire] = []

    for ibuf in ibufs:
        buf_output = ibuf["out"]
        buf_input = ibuf["in"]

        if buf_input not in node_con:
            node_con[buf_input] = []

        current_consumer = node_con[buf_input]
        if buf_output not in current_consumer:
            current_consumer.append(buf_output)

        node_con[buf_input] = current_consumer

    for obuf in obufs:
        buf_output = obuf["out"]
        buf_input = obuf["in"]

        if buf_input not in node_con:
            node_con[buf_input] = []

        current_consumer = node_con[buf_input]
        if buf_output not in current_consumer:
            current_consumer.append(buf_output)

        node_con[buf_input] = current_consumer

    for lut in luts:
        lut_output = lut["output"]
        lut_inputs = lut["inputs"]

        for ins in lut_inputs:
            if ins not in node_con:
                node_con[ins] = []

            current_consumer = node_con[ins]
            if lut_output not in current_consumer:
                current_consumer.append(lut_output)

            node_con[ins] = current_consumer

    return(node_con)
