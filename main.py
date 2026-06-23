from lib import *


# Ignore Auto Window Scaling
ignore_auto_scaling()

# Load File
file_path = select_file()

# Step 1: Parse The Net List ----------------------------------------------------------------------------------------
data = read_vo_file_regex(file_path)

comments = ["DEBUG: ", ""]

comments = comments + data["comments"]; module_name = data["module_name"]; inputs = data["inputs"]; outputs = data["outputs"]
wires = data["wires"]; luts = data["luts"]; ibufs = data["ibufs"]; obufs = data["obufs"]

# Step 2: Build Dependency Graph ------------------------------------------------------------------------------------

# Find Dependencies
node_dep = find_dependencies(inputs, outputs, wires, ibufs, obufs, luts)
# Find Consumers
node_con = find_consumers(inputs, outputs, wires, ibufs, obufs, luts)
# Find Dep Count
dep_count = find_dep_count(node_dep)

# Topological Sort
unresolved_counts = dep_count
execution_order = topological_sort(unresolved_counts, node_con)

# Add Any Missing Outputs To Topological Sort
for lut in luts:
    lut_output = lut["output"].strip() # .strip() removes hidden trailing spaces!
    if lut_output and (lut_output not in execution_order):
        execution_order.append(lut_output)

# 2. Force any Output Buffer destinations into the execution order
for obuf in obufs:
    buf_output = obuf["out"].strip()
    if buf_output and (buf_output not in execution_order):
        execution_order.append(buf_output)

clear_console()

# Sort Inputs & Outputs
inputs = sort_pins_msb_first(inputs)
outputs = sort_pins_msb_first(outputs)

# Step 3: Lut Logic Evaluator
lut_lookup = generate_lut_lookup(luts)

ibufs_map = {b["in"]: b["out"] for b in ibufs} # Raw Pin -> internal _d wire
obufs_map = {b["in"]: b["out"] for b in obufs} # Internal _d wire -> Raw Pin

# Calculate Column Widths and Add Padding

header_string, divider_string, input_widths, output_widths = generate_headers(inputs, outputs)

# Step 4: Simulate and Generate Truth Table

# Get UI TABLE
HEADERS, table_rows = run_sim_ui(execution_order, inputs, outputs, ibufs_map, obufs_map, lut_lookup, input_widths, output_widths)

column_widths_chars = {**input_widths, **output_widths, "||": 2}
PIXEL_PADDING = 25
CHARACTER_PIXEL_WIDTH = 11

# BEGIN GRAPHICS INITIALISATION
wnd = Window((1920, 1080), "FPGA Truther")
WIDTH, HEIGHT = wnd.size

# TAB SYSTEM CONFIG
MODES = ["Truth Table", "Live Tester", "Waveform"]
current_mode = "Truth Table"

# Properties

BG_COLOR = (30, 30, 30)
TEXT_COLOR = (220, 220, 220)
HEADER_BG = (45, 45, 48)
HEADER_TEXT = (0, 255, 100)
LINE_COLOR = (70, 70, 70)

TAB_BAR_HEIGHT = 30
TAB_WIDTH = WIDTH // len(MODES)
TAB_BG_COLOR = (30, 30, 30)
TAB_ACTIVE_COLOR = (45, 45, 48)
TAB_TEXT_INACTIVE = (150, 150, 150)
TAB_TEXT_ACTIVE = (0, 255, 100)

# Surface Definitions
truth_table_surface = pygame.Surface((WIDTH/3*2, HEIGHT-TAB_BAR_HEIGHT))
live_tester_surface = pygame.Surface((WIDTH/3*2, HEIGHT-TAB_BAR_HEIGHT))
debug_surface = pygame.Surface((WIDTH/3, HEIGHT-TAB_BAR_HEIGHT))

# Font Definition
FONT_SIZE = 20
consolas = pygame.font.SysFont(["consolas", "cascadiacode", "courier"], FONT_SIZE)
sans = pygame.font.SysFont("sans-serif", FONT_SIZE*2)

# SCROLL BAR INIT
SCROLLBAR_WIDTH = 8
SCROLLBAR_X = truth_table_surface.get_width() - SCROLLBAR_WIDTH - 5
SCROLLBAR_COLOR = (80, 80, 80)
SCROLLBAR_THUMB_COLOR = (0, 255, 100)
is_dragging_scrollbar = False

AVALIABLE_WIDTH = truth_table_surface.get_width() - SCROLLBAR_WIDTH - 15

# Table Properties
COL_WIDTH = AVALIABLE_WIDTH // len(HEADERS)
START_X = 5
ROW_HEIGHT = 40
HEADER_HEIGHT = 40

COLUMN_PIXELS = []
current_x = START_X
for header in HEADERS:
    COLUMN_PIXELS.append((current_x, COL_WIDTH))
    current_x += COL_WIDTH

scroll_y = 0
scroll_speed = 15
max_visible_rows = (truth_table_surface.get_height() - HEADER_HEIGHT) // ROW_HEIGHT
max_scroll = max(0, (len(table_rows) * ROW_HEIGHT) - (truth_table_surface.get_height() - HEADER_HEIGHT - 20))


# Live Tester
current_pin_states = {pin: 0 for pin in inputs}
current_output_states = evaluate_single_state(
    current_pin_states, execution_order, inputs, outputs, ibufs_map, obufs_map, lut_lookup
)
BOX_WIDTH = 220
BOX_HEIGHT = 45
BOX_PADDING = 15

running = True
while running:
    wnd.screen.fill(BG_COLOR)
    debug_surface.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click
                mouse_x, mouse_y = event.pos

                if current_mode == "Truth Table" and mouse_y > TAB_BAR_HEIGHT:
                    rel_mouse_x = mouse_x - (WIDTH / 3)
                    rel_mouse_y = mouse_y - TAB_BAR_HEIGHT
                    if SCROLLBAR_X <= rel_mouse_x <= SCROLLBAR_X + SCROLLBAR_WIDTH:
                        if thumb_y <= rel_mouse_y <= thumb_y + thumb_height:
                            is_dragging_scrollbar = True

                # TAB BAR
                if mouse_y < TAB_BAR_HEIGHT:
                    tab_idx = mouse_x // TAB_WIDTH
                    if tab_idx < len(MODES):
                        current_mode = MODES[tab_idx]
                    continue

                # Live Tester
                if current_mode == "Live Tester" and mouse_y > TAB_BAR_HEIGHT:
                    rel_mouse_x = mouse_x - (WIDTH / 3)
                    rel_mouse_y = mouse_y - TAB_BAR_HEIGHT

                    for idx, pin in enumerate(inputs):
                        btn_y = 40 + idx * (BOX_HEIGHT + BOX_PADDING)

                        if 20 <= rel_mouse_x <= 20 + BOX_WIDTH:
                            if btn_y <= rel_mouse_y <= btn_y + BOX_HEIGHT:
                                current_pin_states[pin] = 1 - current_pin_states[pin]

                                current_output_states = evaluate_single_state(
                                    current_pin_states, execution_order, inputs,
                                    outputs, ibufs_map, obufs_map, lut_lookup
                                )
                                break

            elif event.button == 4: # Scroll Up
                if current_mode == "Truth Table":
                    scroll_y = max(0, scroll_y - scroll_speed)
            elif event.button == 5: # Scroll Down
                if current_mode == "Truth Table":
                    scroll_y = min(max_scroll, scroll_y + scroll_speed)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_dragging_scrollbar = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if current_mode == "Truth Table":
                    scroll_y = max(0, scroll_y - scroll_speed)
            elif event.key == pygame.K_DOWN:
                if current_mode == "Truth Table":
                    scroll_y = min(max_scroll, scroll_y + scroll_speed)
            elif event.key == pygame.K_p and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if current_mode == "Truth Table":
                    print("Generating Print Document")
                    comments.append("Generating Print Document")
                    export_and_print_table(HEADERS, table_rows, module_name)

    # TOP BAR
    for idx, mode_name in enumerate(MODES):
        tab_x = idx * TAB_WIDTH
        is_active = (current_mode == mode_name)

        bg_color = TAB_ACTIVE_COLOR if is_active else BG_COLOR

        if is_active:
            pygame.draw.rect(wnd.screen, bg_color, (tab_x, 0, TAB_WIDTH, TAB_BAR_HEIGHT), border_radius=10)
            pygame.draw.aaline(wnd.screen, TAB_TEXT_ACTIVE, (tab_x, TAB_BAR_HEIGHT-1), (tab_x+ TAB_WIDTH, TAB_BAR_HEIGHT-1))
        else:
            pygame.draw.rect(wnd.screen, bg_color, (tab_x, 0, TAB_WIDTH, TAB_BAR_HEIGHT-5), border_radius=10)

        #pygame.draw.line(wnd.screen, LINE_COLOR, (tab_x + TAB_WIDTH, 0), (tab_x + TAB_WIDTH, TAB_BAR_HEIGHT), 1)

        text_color = TAB_TEXT_ACTIVE if is_active else TAB_TEXT_INACTIVE
        tab_surf = consolas.render(mode_name, True, text_color)

        render_x = tab_x + (TAB_WIDTH // 2) - (tab_surf.get_width() // 2)
        render_y = (TAB_BAR_HEIGHT // 2) - (tab_surf.get_height() // 2)
        wnd.screen.blit(tab_surf, (render_x, render_y))

    #pygame.draw.line(wnd.screen, LINE_COLOR, (0, TAB_BAR_HEIGHT), (WIDTH, TAB_BAR_HEIGHT), 2)

    if current_mode == "Truth Table":
        truth_table_surface.fill(BG_COLOR)
        # Scroll Bar Movement
        if is_dragging_scrollbar:
            _, mouse_y = pygame.mouse.get_pos()

            rel_mouse_y = mouse_y - TAB_BAR_HEIGHT

            track_y = rel_mouse_y - HEADER_HEIGHT - (thumb_height // 2)
            track_travel = track_height - thumb_height

            if track_travel > 0:
                drag_ratio = max(0.0, min(1.0, track_y / track_travel))
                scroll_y = int(drag_ratio * max_scroll)

        start_idx = scroll_y // ROW_HEIGHT
        end_idx = min(len(table_rows), start_idx + max_visible_rows + 2)

        for i in range(start_idx, end_idx):
            row_inputs, row_outputs = table_rows[i]
            all_bits = row_inputs + ["||"] + row_outputs

            y_pos = HEADER_HEIGHT + (i*ROW_HEIGHT) - scroll_y

            if i % 2 == 0:
                pygame.draw.rect(truth_table_surface, (35,35,35), (0,y_pos, truth_table_surface.get_width(), ROW_HEIGHT))

            for col_idx, bit in enumerate(all_bits):
                col_x, col_w = COLUMN_PIXELS[col_idx]
                col_center_x = col_x + (col_w // 2)

                if bit == "1":
                    color = (200, 200, 200)
                else:
                    color = (120, 120, 120)
                #color = (120, 120, 120) if bit == "||" else TEXT_COLOR
                text_surf = consolas.render(bit, True, color)

                render_x = col_center_x - (text_surf.get_width() // 2)
                render_y = y_pos + (ROW_HEIGHT // 2) - (text_surf.get_height() // 2)
            
                truth_table_surface.blit(text_surf, (render_x, render_y))

            pygame.draw.line(truth_table_surface, LINE_COLOR, (0, y_pos + ROW_HEIGHT), (truth_table_surface.get_width(), y_pos + ROW_HEIGHT), 1)

        # Sticky Header
        pygame.draw.rect(truth_table_surface, HEADER_BG, (0, 0, truth_table_surface.get_width(), HEADER_HEIGHT))
        pygame.draw.line(truth_table_surface, LINE_COLOR, (0, HEADER_HEIGHT), (truth_table_surface.get_width(), HEADER_HEIGHT), 2)

        for col_idx, header in enumerate(HEADERS):
            col_x, col_w = COLUMN_PIXELS[col_idx]
            col_center_x = col_x + (col_w // 2)

            color = TEXT_COLOR if header == "||" else HEADER_TEXT
            text_surf = sans.render(header, True, color)

            render_x = col_center_x - (text_surf.get_width() // 2)
            render_y = (HEADER_HEIGHT // 2) - (text_surf.get_height() // 2)

            truth_table_surface.blit(text_surf, (render_x, render_y))

        # Scroll Bar
        track_height = truth_table_surface.get_height() - HEADER_HEIGHT

        total_data_height = len(table_rows) * ROW_HEIGHT
        if total_data_height > track_height:
            visible_ratio = track_height / total_data_height

            thumb_height = max(20, int(track_height * visible_ratio))

            scroll_ratio = scroll_y / max_scroll
            max_thumb_travel = track_height - thumb_height

            thumb_y = HEADER_HEIGHT + int(max_thumb_travel * scroll_ratio)

            pygame.draw.rect(truth_table_surface, (40, 40, 40), (SCROLLBAR_X, HEADER_HEIGHT, SCROLLBAR_WIDTH, track_height))

            pygame.draw.rect(truth_table_surface, SCROLLBAR_THUMB_COLOR, (SCROLLBAR_X, thumb_y, SCROLLBAR_WIDTH, thumb_height), border_radius=4)

        wnd.screen.blit(truth_table_surface, (WIDTH/3, TAB_BAR_HEIGHT))

    if current_mode == "Live Tester":
        live_tester_surface.fill(BG_COLOR)
        input_title = consolas.render("INPUT CONTROLS (CLICK TO TOGGLE)", True, (150, 150, 150))
        output_title = consolas.render("LIVE SIMULATION OUTPUTS", True, (150, 150, 150))
        live_tester_surface.blit(input_title, (40, 15))
        live_tester_surface.blit(output_title, (WIDTH // 2 + 40, 15))

        pygame.draw.line(live_tester_surface, LINE_COLOR, (WIDTH // 2, 0), (WIDTH // 2, live_tester_surface.get_height()), 1)

        for idx, pin in enumerate(inputs):
            btn_y = 40 + idx * (BOX_HEIGHT + BOX_PADDING)
            state = current_pin_states[pin]

            box_x = 40
            box_color = (0, 150, 60) if state == 1 else (45, 45, 50)
            pygame.draw.rect(live_tester_surface, box_color, (box_x, btn_y, BOX_WIDTH, BOX_HEIGHT), border_radius=6)
            pygame.draw.rect(live_tester_surface, LINE_COLOR, (box_x, btn_y, BOX_WIDTH, BOX_HEIGHT), width=1, border_radius=6)

            lbl_surf = consolas.render(f"{pin} = {state}", True, (255,255,255))
            render_x = box_x + 20
            render_y = btn_y + (BOX_HEIGHT // 2) - (lbl_surf.get_height() // 2)
            live_tester_surface.blit(lbl_surf, (render_x, render_y))

        for idx, pin in enumerate(outputs):
            out_y = 40 + idx * (BOX_HEIGHT + BOX_PADDING)
            state = current_output_states[pin]

            box_color = (15, 35, 20) if state == 1 else (30, 30, 32)
            border_color = HEADER_TEXT if state == 1 else LINE_COLOR

            out_x = WIDTH // 2 + 40
            pygame.draw.rect(live_tester_surface, box_color, (out_x, out_y, BOX_WIDTH, BOX_HEIGHT), border_radius=6)
            pygame.draw.rect(live_tester_surface, border_color, (out_x, out_y, BOX_WIDTH, BOX_HEIGHT), width=1, border_radius=6)

            # Print Output State
            text_color = HEADER_TEXT if state == 1 else TEXT_COLOR
            out_surf = consolas.render(f"{pin} -> {state}", True, text_color)
            render_x = out_x + 20
            render_y = out_y + (BOX_HEIGHT // 2) - (out_surf.get_height() // 2)
            live_tester_surface.blit(out_surf, (render_x, render_y))

        wnd.screen.blit(live_tester_surface, (WIDTH/3, TAB_BAR_HEIGHT))

    # DEBUG
    for i, lines in enumerate(comments):
        text = consolas.render(lines, True, (255,255,255))
        text_rect = text.get_rect()
        text_rect.topleft = (2, i*20)
        debug_surface.blit(text, text_rect)

    wnd.screen.blit(debug_surface, (0,TAB_BAR_HEIGHT))

    pygame.draw.aaline(wnd.screen, (255,255,255), (WIDTH/3, TAB_BAR_HEIGHT), (WIDTH/3, HEIGHT))

    pygame.display.flip()
    wnd.clock.tick(60)

pygame.quit()