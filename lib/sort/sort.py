from collections import deque
import re

def topological_sort(unresolved_counts, node_con):
    ready_pool = deque([wire for wire, count in unresolved_counts.items() if count == 0])

    execution_order = []

    while ready_pool:
        current_wire = ready_pool.popleft()
        execution_order.append(current_wire)

        for consumer in node_con.get(current_wire, []):
            unresolved_counts[consumer] -= 1

            if unresolved_counts[consumer] == 0:
                ready_pool.append(consumer)

    print(" --- TOPOLOGICAL SORT COMPLETE ---")
    return execution_order

def sort_pins_msb_first(pin_list):
    def sort_key(pin):
        # Match names ending in numbers, optionally wrapped in brackets like q or q3
        match = re.match(r"^(.*?)\[?(\d+)\]?$", pin)
        if match:
            prefix, num_str = match.groups()
            # Sort alphabetically by prefix first, then descending (-int) by bus index
            return (prefix, -int(num_str))
        
        # Fallback if no trailing bus index is found
        return (pin, 1)
        
    return sorted(pin_list, key=sort_key)