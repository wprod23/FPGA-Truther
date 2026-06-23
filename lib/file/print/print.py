import os
import webbrowser
import time

def export_and_print_table(headers, rows, module):
    clean_name = module.split(" ")[1] if " " in module else module
    filename = f"{clean_name}_truth_table.html"

    # Read Modular Template
    try:
        with open("lib/file/print/template.html", "r", encoding="utf-8") as f:
            html_template = f.read()
        with open("lib/file/print/style.css", "r", encoding="utf-8") as f:
            css_styles = f.read()
    except FileNotFoundError:
        print("Error: template.html or style.css NOT Found In Project Directory")
        return
    
    table_strings = []

    table_strings.append("<tr>")
    for h in headers:
        if h == "||":
            table_strings.append("<th class='divider'>||</th>")
        else:
            table_strings.append(f"<th>{h}</th>")
    table_strings.append("</tr>")

    for row_inputs, row_outputs in rows:
        table_strings.append("<tr>")
        for inp in row_inputs:
            table_strings.append(f"<td>{inp}</td>")
        table_strings.append("<td class='divider'>||</td>")
        for out in row_outputs:
            table_strings.append(f"<td>{out}</td>")
        table_strings.append("</tr>")

    full_table_html = "\n".join(table_strings)

    final_html = html_template.replace("/*STYLE*/", css_styles)
    final_html = final_html.replace("/*MODULENAME*/", clean_name)
    final_html = final_html.replace("/*TABLE*/", full_table_html)

    with open(filename, "w", encoding='utf-8') as f:
        f.write(final_html)

    webbrowser.open('file://' + os.path.realpath(filename))

    time.sleep(2)

    os.remove(filename)