#!/usr/bin/env python3
"""KiCAD to Lcapy Converter GUI"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).parent))

from kicad_converter.converter import KiCADConverter
from kicad_converter.svg_generator import SVGCircuitGenerator, PNGCircuitGenerator


class KiCADConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KiCAD to Lcapy Converter")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        self.kicad_file = tk.StringVar()
        self.output_dir = tk.StringVar(value=str(Path.cwd()))
        self.output_netlist = tk.BooleanVar(value=True)
        self.output_svg = tk.BooleanVar(value=True)
        self.output_png = tk.BooleanVar(value=False)
        self.output_pdf = tk.BooleanVar(value=False)
        
        self._build_ui()
    
    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="KiCAD to Lcapy Converter", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        ttk.Label(main_frame, text="KiCAD File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.kicad_file, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self._browse_file).grid(row=1, column=2, pady=5)
        
        ttk.Label(main_frame, text="Output Folder:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_dir, width=40).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Browse...", command=self._browse_dir).grid(row=2, column=2, pady=5)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky='ew', pady=15)
        
        ttk.Label(main_frame, text="Output Formats:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(checkbox_frame, text="Netlist (.txt)", variable=self.output_netlist).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checkbox_frame, text="SVG", variable=self.output_svg).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checkbox_frame, text="PNG", variable=self.output_png).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(checkbox_frame, text="PDF", variable=self.output_pdf).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky='ew', pady=15)
        
        convert_btn = ttk.Button(main_frame, text="Convert", command=self._convert, width=20)
        convert_btn.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="gray")
        status_label.grid(row=7, column=0, columnspan=3, pady=5)
    
    def _browse_file(self):
        filepath = filedialog.askopenfilename(
            title="Select KiCAD Schematic",
            filetypes=[("KiCAD Schematics", "*.kicad_sch *.sch"), ("All Files", "*.*")]
        )
        if filepath:
            self.kicad_file.set(filepath)
            self.output_dir.set(str(Path(filepath).parent))
    
    def _browse_dir(self):
        dirpath = filedialog.askdirectory(title="Select Output Folder")
        if dirpath:
            self.output_dir.set(dirpath)
    
    def _convert(self):
        kicad_path = self.kicad_file.get()
        out_dir = self.output_dir.get()
        
        if not kicad_path:
            messagebox.showerror("Error", "Please select a KiCAD file")
            return
        
        if not Path(kicad_path).exists():
            messagebox.showerror("Error", f"File not found: {kicad_path}")
            return
        
        ext = Path(kicad_path).suffix.lower()
        if ext not in ('.sch', '.kicad_sch'):
            messagebox.showerror("Error", "Invalid file type. Please select a .sch or .kicad_sch file")
            return
        
        if not any([self.output_netlist.get(), self.output_svg.get(), 
                    self.output_png.get(), self.output_pdf.get()]):
            messagebox.showerror("Error", "Please select at least one output format")
            return
        
        self.status_var.set("Converting...")
        self.root.update()
        
        try:
            base_name = Path(kicad_path).stem
            out_path = Path(out_dir)
            out_path.mkdir(parents=True, exist_ok=True)
            
            files_created = []
            
            converter = KiCADConverter(kicad_path)
            netlist, components = converter.convert()
            
            if self.output_netlist.get():
                netlist_file = out_path / f"{base_name}_netlist.txt"
                converter.save_netlist(str(netlist_file))
                files_created.append(f"Netlist: {netlist_file.name}")
            
            if self.output_svg.get():
                svg_file = out_path / f"{base_name}.svg"
                svg_gen = SVGCircuitGenerator(kicad_path)
                svg_gen.generate_svg(str(svg_file))
                files_created.append(f"SVG: {svg_file.name}")
            
            if self.output_png.get():
                png_file = out_path / f"{base_name}.png"
                png_gen = PNGCircuitGenerator(kicad_path)
                png_gen.generate_png(str(png_file))
                files_created.append(f"PNG: {png_file.name}")
            
            if self.output_pdf.get():
                png_file = out_path / f"{base_name}.png"
                pdf_file = out_path / f"{base_name}.pdf"
                
                if not png_file.exists():
                    png_gen = PNGCircuitGenerator(kicad_path)
                    png_gen.generate_png(str(png_file))
                
                try:
                    from PIL import Image
                    img = Image.open(png_file)
                    rgb_img = img.convert('RGB')
                    rgb_img.save(str(pdf_file), 'PDF')
                    files_created.append(f"PDF: {pdf_file.name}")
                except ImportError:
                    messagebox.showwarning("Warning", "PDF generation requires Pillow. Install: pip install Pillow")
            
            self.status_var.set("Done!")
            messagebox.showinfo("Success", 
                f"Converted {len(components)} components\n\nFiles created:\n" + "\n".join(files_created))
            
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Conversion Error", str(e))


def main():
    root = tk.Tk()
    app = KiCADConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
