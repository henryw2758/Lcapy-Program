# import script for KiCAD schematic files (.kicad_sch) into
# CircuiTikz either for use in a LaTeX document
# or as basis for Manim animations
#
# Ported to the new S-expression format (.kicad_sch) by [you], 2024
# Original script by Uwe Zimmermann, Uppsala, 2022-08-05

import re
import math
import os
import subprocess
import tempfile

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

filename = r"C:\Users\Khori\OneDrive\Desktop\ex_output\example_2.kicad_sch"

export = "image"   # "image" | "raw" | "manim"

# Output image path (only used when export = "image").
# Defaults to same folder/name as input file but with .png extension.
output_image = os.path.splitext(filename)[0] + ".png"

# DPI for the rendered PNG (higher = larger/sharper image)
image_dpi = 300

# Scale factor: KiCAD mm -> circuitikz cm
sf = 0.25

# CircuiTikz minimum component length in cm.
MIN_COMPONENT_LENGTH = 1.2  # cm

# ---------------------------------------------------------------------------
# Minimal S-expression tokeniser / parser
# ---------------------------------------------------------------------------

def tokenise(text):
    text = text.replace('(', ' ( ').replace(')', ' ) ')
    tokens = []
    for tok in re.split(r'(\s+|"[^"]*")', text):
        tok = tok.strip()
        if tok:
            tokens.append(tok)
    return tokens


def parse(tokens, pos=0):
    if tokens[pos] == '(':
        pos += 1
        lst = []
        while tokens[pos] != ')':
            node, pos = parse(tokens, pos)
            lst.append(node)
        pos += 1
        return lst, pos
    else:
        tok = tokens[pos]
        if tok.startswith('"') and tok.endswith('"'):
            tok = tok[1:-1]
        return tok, pos + 1


def parse_sexp(text):
    tokens = tokenise(text)
    tree, _ = parse(tokens, 0)
    return tree


def find_children(node, key):
    return [child for child in node[1:] if isinstance(child, list) and child and child[0] == key]


def find_child(node, key):
    results = find_children(node, key)
    return results[0] if results else None

# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def rotate_point(x, y, angle_deg):
    rad = math.radians(angle_deg)
    rx = x * math.cos(rad) - y * math.sin(rad)
    ry = x * math.sin(rad) + y * math.cos(rad)
    return rx, ry


def component_endpoints(cx, cy, angle_deg, dx, dy):
    length = math.hypot(dx, dy)
    if length > 0:
        scaled = length * sf
        scale_factor = (MIN_COMPONENT_LENGTH / 2) / length if scaled < MIN_COMPONENT_LENGTH / 2 else sf
        dx_s = dx * scale_factor
        dy_s = dy * scale_factor
    else:
        dx_s, dy_s = 0.0, 0.0
    rx, ry = rotate_point(dx_s, dy_s, -angle_deg)
    wx = cx * sf + rx
    wy = cy * sf + ry
    return wx, -wy


# ---------------------------------------------------------------------------
# Device classification
# ---------------------------------------------------------------------------

def classify_device(lib_id):
    name = lib_id.split(':')[-1].strip()
    mappings = [
        (r'^R$',           'R'),
        (r'^C$',           'C'),
        (r'^L$',           'L'),
        (r'^D$',           'D'),
        (r'^D_Zener$',     'DZ'),
        (r'^D_Schottky$',  'DS'),
        (r'^LED$',         'LED'),
        (r'^VDC$',         'VDC'),
        (r'^VSIN$',        'VSIN'),
        (r'^IDC$',         'IDC'),
        (r'^ISIN$',        'ISIN'),
        (r'^Q_NPN.*$',     'NPN'),
        (r'^Q_NMOS_DSG$',  'NMOS'),
        (r'^Earth$',       'GND'),
        (r'^PWR_FLAG$',    'SKIP'),
    ]
    for pattern, key in mappings:
        if re.match(pattern, name, re.IGNORECASE):
            return key
    return 'UNKNOWN'


def kicad_angle_to_circuitikz(angle_deg):
    return int((-angle_deg) % 360)

# ---------------------------------------------------------------------------
# Parse the schematic file
# ---------------------------------------------------------------------------

with open(filename, 'r', encoding='utf-8') as f:
    raw_text = f.read()

tree = parse_sexp(raw_text)
latexoutput = []

for node in tree[1:]:
    if not isinstance(node, list) or not node:
        continue
    tag = node[0]

    if tag == 'wire':
        pts_node = find_child(node, 'pts')
        if pts_node is None:
            continue
        xys = find_children(pts_node, 'xy')
        if len(xys) < 2:
            continue
        x0, y0 = float(xys[0][1]), float(xys[0][2])
        x1, y1 = float(xys[1][1]), float(xys[1][2])
        latexoutput.append(
            r"\draw ({:.4f},{:.4f}) -- ({:.4f},{:.4f});".format(
                x0 * sf, -y0 * sf, x1 * sf, -y1 * sf))

    elif tag == 'symbol':
        lib_id_node = find_child(node, 'lib_id')
        if lib_id_node is None:
            continue
        lib_id = lib_id_node[1]

        at_node = find_child(node, 'at')
        if at_node is None:
            continue
        cx    = float(at_node[1])
        cy    = float(at_node[2])
        angle = float(at_node[3]) if len(at_node) > 3 else 0.0

        label = ''
        value = ''
        for prop in find_children(node, 'property'):
            if len(prop) < 3:
                continue
            if prop[1] == 'Reference':
                label = prop[2]
            elif prop[1] == 'Value':
                value = prop[2]

        dev = classify_device(lib_id)
        if dev == 'SKIP':
            continue

        PIN_V  = 3.81
        PIN_H  = 3.81
        PIN_VS = 5.08

        if dev == 'R':
            x1, y1 = component_endpoints(cx, cy, angle,  0, +PIN_V)
            x2, y2 = component_endpoints(cx, cy, angle,  0, -PIN_V)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[R, l=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'C':
            x1, y1 = component_endpoints(cx, cy, angle,  0, +PIN_V)
            x2, y2 = component_endpoints(cx, cy, angle,  0, -PIN_V)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[C, l=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'L':
            x1, y1 = component_endpoints(cx, cy, angle,  0, +PIN_V)
            x2, y2 = component_endpoints(cx, cy, angle,  0, -PIN_V)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[american inductor, l=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'D':
            x1, y1 = component_endpoints(cx, cy, angle, +PIN_H,  0)
            x2, y2 = component_endpoints(cx, cy, angle, -PIN_H,  0)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[Do, l=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'DZ':
            x1, y1 = component_endpoints(cx, cy, angle, +PIN_H,  0)
            x2, y2 = component_endpoints(cx, cy, angle, -PIN_H,  0)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[zDo, l=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'DS':
            x1, y1 = component_endpoints(cx, cy, angle, +PIN_H,  0)
            x2, y2 = component_endpoints(cx, cy, angle, -PIN_H,  0)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[sDo, l=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'LED':
            x1, y1 = component_endpoints(cx, cy, angle, +PIN_H,  0)
            x2, y2 = component_endpoints(cx, cy, angle, -PIN_H,  0)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[leDo, l=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'VDC':
            x1, y1 = component_endpoints(cx, cy, angle,  0, -PIN_VS)
            x2, y2 = component_endpoints(cx, cy, angle,  0, +PIN_VS)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[V, v=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'VSIN':
            x1, y1 = component_endpoints(cx, cy, angle,  0, -PIN_VS)
            x2, y2 = component_endpoints(cx, cy, angle,  0, +PIN_VS)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[sV, v=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'IDC':
            x1, y1 = component_endpoints(cx, cy, angle,  0, +PIN_VS)
            x2, y2 = component_endpoints(cx, cy, angle,  0, -PIN_VS)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[I, i=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'ISIN':
            x1, y1 = component_endpoints(cx, cy, angle,  0, +PIN_VS)
            x2, y2 = component_endpoints(cx, cy, angle,  0, -PIN_VS)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) to[sI, i=${}$, a=${}$] ({:.4f},{:.4f});".format(x1, y1, label, value, x2, y2))
        elif dev == 'GND':
            wx, wy = component_endpoints(cx, cy, angle, 0, 0)
            rot = kicad_angle_to_circuitikz(angle)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) node[ground, rotate={}]{{}};".format(wx, wy, rot))
        elif dev == 'NPN':
            x1, y1 = component_endpoints(cx, cy, angle, 2.54, 0)
            rot = kicad_angle_to_circuitikz(angle)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) node[npn, rotate={}]{{{}}};".format(x1, y1, rot, label))
        elif dev == 'NMOS':
            x1, y1 = component_endpoints(cx, cy, angle, 2.54, 0)
            rot = kicad_angle_to_circuitikz(angle)
            latexoutput.append(r"\draw ({:.4f},{:.4f}) node[nigfete, rotate={}]{{{}}};".format(x1, y1, rot, label))
        else:
            latexoutput.append(r"% UNKNOWN device '{}': \draw ({:.4f},{:.4f}) node[]{{{}}};".format(lib_id, cx * sf, -cy * sf, label))

# ---------------------------------------------------------------------------
# Normalise: shift all coordinates so bbox starts at (MARGIN, MARGIN)
# ---------------------------------------------------------------------------

MARGIN = 0.5  # cm
coord_re = re.compile(r'\((-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\)')

all_x, all_y = [], []
for row in latexoutput:
    if row.startswith('%'):
        continue
    for mx, my in coord_re.findall(row):
        all_x.append(float(mx))
        all_y.append(float(my))

shift_x = (MARGIN - min(all_x)) if all_x else 0.0
shift_y = (MARGIN - min(all_y)) if all_y else 0.0

def shift_coords(line):
    if line.startswith('%'):
        return line
    def replacer(m):
        return '({:.4f},{:.4f})'.format(float(m.group(1)) + shift_x, float(m.group(2)) + shift_y)
    return coord_re.sub(replacer, line)

normalised = [shift_coords(row) for row in latexoutput]

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

latex_body = "\n".join("  " + row for row in normalised)

TEX_TEMPLATE = r"""\documentclass[border=20pt]{{standalone}}
\usepackage{{circuitikz}}
\begin{{document}}
\begin{{circuitikz}}[american]
{body}
\end{{circuitikz}}
\end{{document}}
"""

if export == "raw":
    print(r"\begin{circuitikz}")
    for row in normalised:
        print("  " + row)
    print(r"\end{circuitikz}")

elif export == "manim":
    print("        circuit = MathTex(")
    for row in normalised:
        print('            r"{}",'.format(row))
    print('''
            stroke_width=4,
            fill_opacity=0,
            stroke_opacity=1,
            tex_environment="circuitikz",
            tex_template=template,
            )''')

elif export == "image":
    # Requirements:
    #   - pdflatex   (MiKTeX: https://miktex.org  or TeX Live)
    #   - pdftoppm   (Poppler: https://github.com/oschwartz10612/poppler-windows/releases)
    #   - pdf2svg    (https://github.com/jalios/pdf2svg-windows  or  choco install pdf2svg)
    #   - Pillow     (pip install pillow)
    base = os.path.splitext(filename)[0]
    output_pdf = base + ".pdf"
    output_svg = base + ".svg"
    output_png = base + ".png"

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "circuit.tex")
        pdf_path = os.path.join(tmpdir, "circuit.pdf")

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(TEX_TEMPLATE.format(body=latex_body))

        # --- compile LaTeX -> PDF ---
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("pdflatex failed. Log output:")
            print(result.stdout[-3000:])
            raise SystemExit(1)

        # --- copy PDF to output location ---
        import shutil
        shutil.copy(pdf_path, output_pdf)
        print("PDF  saved to: {}".format(os.path.abspath(output_pdf)))

        # --- PDF -> SVG (via pdf2svg) ---
        svg_result = subprocess.run(
            ["pdftocairo", "-svg", pdf_path, output_svg],
            capture_output=True, text=True
        )
        if svg_result.returncode == 0:
            print("SVG  saved to: {}".format(os.path.abspath(output_svg)))
        else:
            print("SVG conversion failed (is pdf2svg installed and on PATH?)")
            print(svg_result.stderr)

        # --- PDF -> PNG (via pdftoppm + Pillow) ---
        ppm_stem = os.path.join(tmpdir, "circuit_out")
        subprocess.run(
            ["pdftoppm", "-r", str(image_dpi), pdf_path, ppm_stem],
            check=True
        )
        ppm_file = ppm_stem + "-1.ppm"
        from PIL import Image
        img = Image.open(ppm_file)
        img.save(output_png)
        print("PNG  saved to: {}".format(os.path.abspath(output_png)))
