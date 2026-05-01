"""Simple GUI for KiCAD to Circuitikz converter and Netlist to Text."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import os
import glob
import shutil
import subprocess

sys.path.insert(0, os.path.dirname(__file__))
from Extractor import convert_kicad_to_circuitikz
from netlist_to_text.circuit import Circuit
from netlist_to_text.parser import detect_format


class ConverterGUI:
    """Simple GUI for the converter."""

    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Converter - KiCAD to Netlist & Netlist to Text")
        self.root.geometry("900x700")

        self.input_file = ""
        self.netlist_file = ""
        self.output_dir = ""
        self.output_name = ""

        self._create_widgets()

    def _create_widgets(self):
        """Create GUI widgets."""

        # Mode selection with checkboxes
        mode_frame = ttk.LabelFrame(self.root, text="Conversion Modes", padding=10)
        mode_frame.pack(fill='x', padx=10, pady=5)

        self.mode_vars = {
            'kicad': tk.BooleanVar(value=True),
            'netlist': tk.BooleanVar(value=False),
        }

        # Bind to enable/disable UI based on selection
        self.kicad_check = ttk.Checkbutton(mode_frame, text="KiCAD Schematic → Circuitikz Diagram",
                                                variable=self.mode_vars['kicad'],
                                                command=self._update_ui_state)
        self.kicad_check.grid(row=0, column=0, padx=20, pady=5, sticky='w')

        self.netlist_check = ttk.Checkbutton(mode_frame, text="Netlist → Text Description",
                                                   variable=self.mode_vars['netlist'],
                                                   command=self._update_ui_state)
        self.netlist_check.grid(row=0, column=1, padx=20, pady=5, sticky='w')

        # KiCAD input section
        self.kicad_frame = ttk.LabelFrame(self.root, text="KiCAD Schematic Input", padding=10)
        self.kicad_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(self.kicad_frame, text="KiCAD schematic file:").grid(row=0, column=0, sticky='w')
        self.input_entry = ttk.Entry(self.kicad_frame, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, sticky='ew')
        button_frame = ttk.Frame(self.kicad_frame)
        button_frame.grid(row=0, column=2, sticky='ew')
        ttk.Button(button_frame, text="Browse...", command=self._browse_input, width=10).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Current Dir", command=self._browse_current_dir, width=10).pack(side='left', padx=2)
        ttk.Button(button_frame, text="List Files", command=self._list_files, width=10).pack(side='left', padx=2)
        ttk.Label(self.kicad_frame, text="(supports .sch and .kicad_sch - or type path directly)", foreground='gray').grid(row=1, column=1, sticky='w')

        # Netlist input section
        self.netlist_frame = ttk.LabelFrame(self.root, text="Netlist Input", padding=10)
        self.netlist_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(self.netlist_frame, text="Netlist file (.net, .cir, .spice):").grid(row=0, column=0, sticky='w')
        self.netlist_entry = ttk.Entry(self.netlist_frame, width=50)
        self.netlist_entry.grid(row=0, column=1, padx=5)
        ttk.Button(self.netlist_frame, text="Browse...", command=self._browse_netlist).grid(row=0, column=2)
        ttk.Label(self.netlist_frame, text="(KiCAD netlist format)", foreground='gray').grid(row=1, column=1, sticky='w')

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

        # KiCAD output format selection
        self.kicad_format_frame = ttk.LabelFrame(self.root, text="Output Formats (KiCAD Mode)", padding=10)
        self.kicad_format_frame.pack(fill='x', padx=10, pady=5)

        self.vars = {
            'pdf': tk.BooleanVar(value=True),
            'png': tk.BooleanVar(value=True),
            'svg': tk.BooleanVar(value=True),
            'tex': tk.BooleanVar(value=True),
        }

        ttk.Checkbutton(self.kicad_format_frame, text="PDF (.pdf)", variable=self.vars['pdf']).grid(row=0, column=0, padx=10, pady=2, sticky='w')
        ttk.Checkbutton(self.kicad_format_frame, text="PNG (.png)", variable=self.vars['png']).grid(row=0, column=1, padx=10, pady=2, sticky='w')
        ttk.Checkbutton(self.kicad_format_frame, text="SVG (.svg)", variable=self.vars['svg']).grid(row=1, column=0, padx=10, pady=2, sticky='w')
        ttk.Checkbutton(self.kicad_format_frame, text="Circuitikz TeX (.tex)", variable=self.vars['tex']).grid(row=1, column=1, padx=10, pady=2, sticky='w')
        ttk.Label(self.kicad_format_frame, text="* Select output formats to generate", foreground='blue').grid(row=2, column=0, columnspan=2, sticky='w', padx=10)

        # Netlist output format selection
        self.netlist_format_frame = ttk.LabelFrame(self.root, text="Output Formats (Netlist Mode)", padding=10)
        # Don't pack yet

        self.netlist_output_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.netlist_format_frame, text="Text Description (.txt)", variable=self.netlist_output_var).grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(self.netlist_format_frame, text="* Generates human-readable circuit description for accessibility", foreground='blue').grid(row=0, column=1, sticky='w')

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

        # Bind Enter key to input field for file validation
        self.input_entry.bind('<FocusOut>', lambda e: self._validate_input_file())
        self.netlist_entry.bind('<FocusOut>', lambda e: self._validate_netlist_file())

        # Initial UI state update
        self._update_ui_state()

    def _update_ui_state(self):
        """Enable/disable UI sections based on mode checkboxes."""
        kicad_enabled = self.mode_vars['kicad'].get()
        netlist_enabled = self.mode_vars['netlist'].get()

        # Enable/disable KiCAD inputs
        state_kicad = 'normal' if kicad_enabled else 'disabled'
        self.input_entry.config(state=state_kicad)
        for child in self.kicad_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state=state_kicad)

        # Enable/disable Netlist inputs
        state_netlist = 'normal' if netlist_enabled else 'disabled'
        self.netlist_entry.config(state=state_netlist)
        for child in self.netlist_frame.winfo_children():
            if isinstance(child, ttk.Button):
                child.config(state=state_netlist)

        # Show/hide output format sections
        self.kicad_format_frame.pack_forget()
        self.netlist_format_frame.pack_forget()

        if kicad_enabled and not netlist_enabled:
            self.kicad_format_frame.pack(fill='x', padx=10, pady=5, after=self.netlist_frame)
            for child in self.kicad_format_frame.winfo_children():
                if isinstance(child, ttk.Checkbutton):
                    child.config(state='normal')

        elif netlist_enabled and not kicad_enabled:
            self.netlist_format_frame.pack(fill='x', padx=10, pady=5, after=self.netlist_frame)
            for child in self.netlist_format_frame.winfo_children():
                if isinstance(child, ttk.Checkbutton):
                    child.config(state='normal')

        elif kicad_enabled and netlist_enabled:
            self.kicad_format_frame.pack(fill='x', padx=10, pady=5, after=self.netlist_frame)
            self.netlist_format_frame.pack(fill='x', padx=10, pady=5, after=self.kicad_format_frame)
            for child in self.kicad_format_frame.winfo_children():
                if isinstance(child, ttk.Checkbutton):
                    child.config(state='normal')
            for child in self.netlist_format_frame.winfo_children():
                if isinstance(child, ttk.Checkbutton):
                    child.config(state='normal')

        # If neither enabled, nothing shows (both sections already pack_forget above)

        # Auto-detect test.kicad_sch when KiCAD mode is enabled
        if kicad_enabled and not self.input_file and os.path.exists("test.kicad_sch"):
            self.input_file = os.path.abspath("test.kicad_sch")
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.input_file)

            # Set output directory
            self.output_dir = os.path.dirname(self.input_file)
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, self.output_dir)

            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            if base_name.endswith('.kicad'):
                base_name = base_name[:-6]
            self.output_name = base_name
            self.output_name_entry.delete(0, tk.END)
            self.output_name_entry.insert(0, base_name)

            if not self.mode_vars['netlist'].get():
                self._log(f"Auto-detected test.kicad_sch\n")

    def _log(self, message):
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)
        self.root.update_idletasks()

    def _validate_input_file(self):
        path = self.input_entry.get().strip()
        if not path:
            return
        if os.path.isfile(path):
            self.input_file = path
            if not self.output_dir_entry.get().strip():
                self.output_dir = os.path.dirname(path)
                self.output_dir_entry.delete(0, tk.END)
                self.output_dir_entry.insert(0, self.output_dir)
            if not self.output_name_entry.get().strip():
                base = os.path.splitext(os.path.basename(path))[0]
                if base.endswith('.kicad'):
                    base = base[:-6]
                self.output_name = base
                self.output_name_entry.delete(0, tk.END)
                self.output_name_entry.insert(0, base)

    def _validate_netlist_file(self):
        path = self.netlist_entry.get().strip()
        if not path:
            return
        if os.path.isfile(path):
            self.netlist_file = path

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Select KiCAD Schematic",
            filetypes=[("KiCAD Schematics", "*.kicad_sch *.sch"), ("All Files", "*.*")]
        )
        if path:
            self.input_file = path
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)
            self._validate_input_file()

    def _browse_current_dir(self):
        sch_files = glob.glob("*.kicad_sch") + glob.glob("*.sch")
        if sch_files:
            self.input_file = os.path.abspath(sch_files[0])
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.input_file)
            self._validate_input_file()
            self._log(f"Found: {sch_files[0]}\n")
        else:
            self._log("No KiCAD schematic files found in current directory.\n")

    def _list_files(self):
        self._log("\n--- KiCAD Schematics in current directory ---\n")
        for ext in ("*.kicad_sch", "*.sch"):
            for f in glob.glob(ext):
                self._log(f"  {os.path.abspath(f)}\n")
        self._log("--- End of list ---\n\n")

    def _browse_output_dir(self):
        path = filedialog.askdirectory(title="Select Output Directory")
        if path:
            self.output_dir = path
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, path)

    def _browse_netlist(self):
        path = filedialog.askopenfilename(
            title="Select Netlist File",
            filetypes=[("Netlist Files", "*.net *.cir *.spice"), ("All Files", "*.*")]
        )
        if path:
            self.netlist_file = path
            self.netlist_entry.delete(0, tk.END)
            self.netlist_entry.insert(0, path)
            self._validate_netlist_file()

    def _convert(self):
        self.output_text.delete('1.0', tk.END)
        output_dir = self.output_dir_entry.get().strip() or os.path.dirname(__file__)
        output_name = self.output_name_entry.get().strip() or "output"

        try:
            self.progress.start(10)

            if self.mode_vars['kicad'].get():
                input_path = self.input_entry.get().strip()
                if not input_path or not os.path.isfile(input_path):
                    self._log("Error: Please specify a valid KiCAD schematic file.\n")
                    return
                self._convert_kicad(input_path, output_dir, output_name)

            if self.mode_vars['netlist'].get():
                netlist_path = self.netlist_entry.get().strip()
                if not netlist_path or not os.path.isfile(netlist_path):
                    self._log("Error: Please specify a valid netlist file.\n")
                    return
                self._convert_netlist(netlist_path, output_dir, output_name)

            self._log("\nDone.\n")
        except Exception as e:
            self._log(f"\nError: {e}\n")
            messagebox.showerror("Conversion Error", str(e))
        finally:
            self.progress.stop()

    def _convert_kicad(self, input_path, output_dir, output_name):
        self._log("Converting KiCAD schematic to Circuitikz diagram...\n")

        want_image = self.vars['pdf'].get() or self.vars['png'].get() or self.vars['svg'].get()
        if want_image:
            try:
                files = convert_kicad_to_circuitikz(input_path, export_mode="image")
                for f in files:
                    dest = os.path.join(output_dir, os.path.basename(f))
                    if os.path.abspath(f) != os.path.abspath(dest):
                        shutil.move(f, dest)
                    self._log(f"  Generated: {dest}\n")
            except (RuntimeError, FileNotFoundError) as e:
                self._log(f"  Image generation failed (pdflatex not found): {e}\n")
                self._log("  Skipping image formats.\n")

        if self.vars['tex'].get():
            files = convert_kicad_to_circuitikz(input_path, export_mode="raw")
            for f in files:
                dest = os.path.join(output_dir, output_name + ".tex")
                if os.path.abspath(f) != os.path.abspath(dest):
                    shutil.move(f, dest)
                self._log(f"  TeX written to: {dest}\n")
                with open(dest, 'r', encoding='utf-8') as tf:
                    self._log("\n--- Circuitikz Preview ---\n")
                    self._log(tf.read())
                    self._log("--- End Preview ---\n")

    def _convert_netlist(self, netlist_path, output_dir, output_name):
        self._log("Parsing netlist file...\n")
        fmt = detect_format(netlist_path)
        self._log(f"  Detected format: {fmt}\n")

        circuit = Circuit()
        circuit.from_netlist_file(netlist_path)
        circuit.rename_nodes()
        description = circuit.generate_description()

        self._log("\n--- Circuit Description ---\n")
        self._log(description)

        if self.netlist_output_var.get():
            txt_path = os.path.join(output_dir, output_name + "_description.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(description)
            self._log(f"  Description written to: {txt_path}\n")


def main():
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()