"""Simple GUI for KiCAD to Circuitikz converter."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from kicad2circuitikz import parse_schematic, CircuitikzExporter
from kicad2circuitikz.pdf_exporter import PDFExporter


class ConverterGUI:
    """Simple GUI for the converter."""

    def __init__(self, root):
        self.root = root
        self.root.title("KiCAD to Circuitikz Converter")
        self.root.geometry("900x700")

        self.input_file = ""
        self.output_dir = ""
        self.output_name = ""

        self._create_widgets()

    def _create_widgets(self):
        """Create GUI widgets."""

        # Input section
        input_frame = ttk.LabelFrame(self.root, text="Input", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(input_frame, text="KiCAD schematic file:").grid(row=0, column=0, sticky='w')
        self.input_entry = ttk.Entry(input_frame, width=50)
        self.input_entry.grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="Browse...", command=self._browse_input).grid(row=0, column=2)
        ttk.Label(input_frame, text="(supports .sch and .kicad_sch)", foreground='gray').grid(row=1, column=1, sticky='w')

        # Output section
        output_frame = ttk.LabelFrame(self.root, text="Output", padding=10)
        output_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(output_frame, text="Output directory:").grid(row=0, column=0, sticky='w')
        self.output_dir_entry = ttk.Entry(output_frame, width=50)
        self.output_dir_entry.grid(row=0, column=1, padx=5)
        ttk.Button(output_frame, text="Browse...", command=self._browse_output_dir).grid(row=0, column=2)

        ttk.Label(output_frame, text="Base name:").grid(row=1, column=0, sticky='w', pady=5)
        self.output_name_entry = ttk.Entry(output_frame, width=50)
        self.output_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Output format selection
        format_frame = ttk.LabelFrame(self.root, text="Output Formats", padding=10)
        format_frame.pack(fill='x', padx=10, pady=5)

        self.vars = {
            'tex': tk.BooleanVar(value=True),
            'netlist': tk.BooleanVar(value=True),
            'pdf': tk.BooleanVar(value=True),
            'png': tk.BooleanVar(value=True),
            'svg': tk.BooleanVar(value=False),
        }

        ttk.Checkbutton(format_frame, text="Circuitikz/LaTeX (.tex)", variable=self.vars['tex']).grid(row=0, column=0, padx=10, pady=5)
        ttk.Checkbutton(format_frame, text="Netlist (.txt)", variable=self.vars['netlist']).grid(row=0, column=1, padx=10, pady=5)
        ttk.Checkbutton(format_frame, text="PDF (.pdf)", variable=self.vars['pdf']).grid(row=1, column=0, padx=10, pady=5)
        ttk.Checkbutton(format_frame, text="PNG (.png)", variable=self.vars['png']).grid(row=1, column=1, padx=10, pady=5)
        ttk.Checkbutton(format_frame, text="SVG (.svg)", variable=self.vars['svg']).grid(row=2, column=0, padx=10, pady=5)
        ttk.Label(format_frame, text="* All formats use matplotlib (no external tools required)", foreground='green').grid(row=2, column=1, sticky='w')

        # Convert button
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        self.convert_button = ttk.Button(button_frame, text="Convert", command=self._convert, width=20)
        self.convert_button.pack()

        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)

        # Output area
        output_frame = ttk.LabelFrame(self.root, text="Output / Preview", padding=10)
        output_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, wrap='word')
        self.output_text.pack(fill='both', expand=True)

    def _browse_input(self):
        """Browse for input schematic file."""
        filename = filedialog.askopenfilename(
            title="Select KiCAD schematic file",
            filetypes=[
                ("KiCAD Schematic", "*.sch *.kicad_sch"),
                ("KiCAD v6+ Schematic", "*.kicad_sch"),
                ("KiCAD v5 Schematic", "*.sch"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_file = filename
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)

            # Set default output directory and name
            self.output_dir = os.path.dirname(filename)
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, self.output_dir)

            base_name = os.path.splitext(os.path.basename(filename))[0]
            if base_name.endswith('.kicad'):
                base_name = base_name[:-6]
            self.output_name = base_name
            self.output_name_entry.delete(0, tk.END)
            self.output_name_entry.insert(0, base_name)

    def _browse_output_dir(self):
        """Browse for output directory."""
        dirname = filedialog.askdirectory(title="Select output directory")
        if dirname:
            self.output_dir = dirname
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, dirname)

    def _convert(self):
        """Convert the schematic."""
        # Validate input
        if not self.input_file:
            messagebox.showerror("Error", "Please select a KiCAD schematic file")
            return

        if not self.output_dir:
            messagebox.showerror("Error", "Please select an output directory")
            return

        if not self.output_name:
            self.output_name = os.path.splitext(os.path.basename(self.input_file))[0]
            if self.output_name.endswith('.kicad'):
                self.output_name = self.output_name[:-6]

        # Disable button and start progress
        self.convert_button.config(state='disabled')
        self.progress.start()
        self.root.update()

        # Clear output area
        self.output_text.delete(1.0, tk.END)
        self._log(f"Parsing {os.path.basename(self.input_file)}...\n")

        try:
            # Parse the schematic (auto-detect format)
            components, wires, parser = parse_schematic(self.input_file)

            self._log(f"Found {len(components)} components\n")
            self._log(f"Found {len(wires)} wires\n\n")

            # Circuitikz/LaTeX
            if self.vars['tex'].get():
                self._log("Generating LaTeX...\n")
                tex_file = os.path.join(self.output_dir, f"{self.output_name}.tex")
                exporter = CircuitikzExporter()
                circuitikz_code = exporter.export(components, wires)

                # Wrap in complete LaTeX document
                full_tex = self._wrap_latex(circuitikz_code)

                with open(tex_file, 'w') as f:
                    f.write(full_tex)

                self._log(f"✓ Saved LaTeX to: {tex_file}\n")

            # Netlist
            if self.vars['netlist'].get():
                self._log("Generating netlist...\n")
                netlist_file = os.path.join(self.output_dir, f"{self.output_name}_netlist.txt")
                netlist = self._generate_netlist(components, wires)

                with open(netlist_file, 'w') as f:
                    f.write(netlist)

                self._log(f"✓ Saved netlist to: {netlist_file}\n")

            # PDF (using matplotlib, no external tools)
            if self.vars['pdf'].get():
                self._log("Generating PDF...\n")
                pdf_file = os.path.join(self.output_dir, f"{self.output_name}.pdf")

                try:
                    pdf_exporter = PDFExporter()
                    pdf_exporter.export(components, wires, pdf_file)
                except Exception as e:
                    self._log(f"✗ PDF generation failed: {str(e)}\n")
                    import traceback
                    self._log(traceback.format_exc())

            # PNG (using matplotlib, no external tools)
            if self.vars['png'].get():
                self._log("Generating PNG...\n")
                png_file = os.path.join(self.output_dir, f"{self.output_name}.png")

                try:
                    pdf_exporter = PDFExporter()
                    pdf_exporter.export(components, wires, png_file)
                except Exception as e:
                    self._log(f"✗ PNG generation failed: {str(e)}\n")
                    import traceback
                    self._log(traceback.format_exc())

            # SVG (using matplotlib, no external tools)
            if self.vars['svg'].get():
                self._log("Generating SVG...\n")
                svg_file = os.path.join(self.output_dir, f"{self.output_name}.svg")

                try:
                    pdf_exporter = PDFExporter()
                    pdf_exporter.export(components, wires, svg_file)
                except Exception as e:
                    self._log(f"✗ SVG generation failed: {str(e)}\n")
                    import traceback
                    self._log(traceback.format_exc())

            # Show preview
            if self.vars['tex'].get():
                self._log("\n" + "="*60 + "\n")
                self._log("Circuitikz Preview:\n")
                self._log("="*60 + "\n")
                exporter = CircuitikzExporter()
                self._log(exporter.export(components, wires))
                self._log("\n" + "="*60 + "\n")

            self._log("\n✓ Conversion complete!\n")

        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
            self._log(f"\n✗ Error: {str(e)}\n")
            import traceback
            self._log(traceback.format_exc())

        finally:
            # Re-enable button and stop progress
            self.convert_button.config(state='normal')
            self.progress.stop()

    def _log(self, message: str):
        """Log a message to the output area."""
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)
        self.root.update()

    def _wrap_latex(self, circuitikz_code: str) -> str:
        """Wrap Circuitikz code in a complete LaTeX document."""
        return f"""\\documentclass[preview]{{standalone}}
\\usepackage{{circuitikz}}
\\begin{{document}}

\\begin{{center}}
{circuitikz_code}
\\end{{center}}

\\end{{document}}
"""

    def _generate_netlist(self, components, wires) -> str:
        """Generate a simple netlist as text file."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"NETLIST for: {os.path.basename(self.input_file)}")
        lines.append("=" * 60)
        lines.append("")
        lines.append("COMPONENTS:")
        lines.append("-" * 40)

        for comp in components:
            if comp.name and not comp.name.startswith('#'):
                lines.append(f"  {comp.name:10} | {comp.type:15} | Value: {comp.value if comp.value else 'N/A':10}")

        lines.append("")
        lines.append("WIRES:")
        lines.append("-" * 40)

        for i, wire in enumerate(wires, 1):
            lines.append(f"  Wire {i:2}: ({wire.x1:4}, {wire.y1:4}) -> ({wire.x2:4}, {wire.y2:4})")

        lines.append("")
        lines.append("=" * 60)
        lines.append(f"Total: {len(components)} components, {len(wires)} wires")
        lines.append("=" * 60)

        return '\n'.join(lines)


def main():
    """Run the GUI."""
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
