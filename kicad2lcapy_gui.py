"""KiCAD to Lcapy Converter - Desktop GUI Application"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import sys
import os
import threading

sys.path.insert(0, str(Path(__file__).parent / 'lcapy'))

from lcapy.kicad.converter import KiCADConverter
from lcapy import Circuit


class KiCADConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KiCAD to Lcapy Converter")
        self.root.geometry("900x700")
        
        self.selected_file = None
        self.output_dir = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create user interface."""
        title = tk.Label(self.root, text="KiCAD to Lcapy Converter", 
                        font=("Arial", 16, "bold"), fg="darkblue")
        title.pack(pady=10)
        
        # File selection
        file_frame = ttk.LabelFrame(self.root, text="Step 1: Select KiCAD File", padding=10)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        self.file_label = tk.Label(file_frame, text="No file selected", fg="gray")
        self.file_label.pack(side="left", fill="x", expand=True)
        
        tk.Button(file_frame, text="Browse...", command=self.browse_file,
                 bg="lightblue", padx=20).pack(side="right", padx=5)
        
        # Output directory
        output_frame = ttk.LabelFrame(self.root, text="Step 2: Choose Output Directory", padding=10)
        output_frame.pack(fill="x", padx=10, pady=10)
        
        self.output_label = tk.Label(output_frame, text="Current directory", fg="gray")
        self.output_label.pack(side="left", fill="x", expand=True)
        
        tk.Button(output_frame, text="Browse...", command=self.browse_output,
                 bg="lightblue", padx=20).pack(side="right", padx=5)
        
        # Options
        options_frame = ttk.LabelFrame(self.root, text="Step 3: Choose Outputs", padding=10)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        self.svg_var = tk.BooleanVar(value=True)
        self.png_var = tk.BooleanVar(value=True)
        self.netlist_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(options_frame, text="SVG Diagram", variable=self.svg_var).pack(anchor="w")
        tk.Checkbutton(options_frame, text="PNG Diagram", variable=self.png_var).pack(anchor="w")
        tk.Checkbutton(options_frame, text="Netlist (TXT)", variable=self.netlist_var).pack(anchor="w")
        
        # Convert button
        convert_frame = tk.Frame(self.root)
        convert_frame.pack(pady=20)
        
        self.convert_btn = tk.Button(convert_frame, text="CONVERT",
                                     command=self.convert, bg="green", fg="white",
                                     font=("Arial", 14, "bold"), padx=40, pady=10)
        self.convert_btn.pack()
        
        # Progress
        self.progress = ttk.Progressbar(self.root, mode='indeterminate', length=400)
        self.progress.pack(pady=10)
        
        # Output text
        output_frame = ttk.LabelFrame(self.root, text="Status / Netlist", padding=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.output_text = tk.Text(output_frame, height=10, wrap="word")
        self.output_text.pack(fill="both", expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status_var, bg="lightgray", height=1).pack(fill="x", side="bottom")
    
    def browse_file(self):
        """Browse for KiCAD file."""
        file = filedialog.askopenfilename(
            title="Select KiCAD Schematic",
            filetypes=[("KiCAD Schematics", "*.kicad_sch"), ("All Files", "*.*")]
        )
        if file:
            self.selected_file = file
            self.file_label.config(text=Path(file).name, fg="black")
            self.status_var.set(f"Selected: {Path(file).name}")
    
    def browse_output(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.output_label.config(text=directory, fg="black")
            self.status_var.set(f"Output: {Path(directory).name}")
    
    def convert(self):
        """Convert the KiCAD file."""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a KiCAD file first")
            return
        
        thread = threading.Thread(target=self._do_convert)
        thread.start()
    
    def _do_convert(self):
        """Perform conversion in background thread."""
        try:
            self.convert_btn.config(state="disabled")
            self.progress.start()
            self.status_var.set("Converting...")
            
            output_dir = self.output_dir or os.getcwd()
            base_name = Path(self.selected_file).stem
            
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Converting KiCAD file...\n")
            self.root.update()
            
            # Convert
            converter = KiCADConverter(self.selected_file)
            netlist, components = converter.convert()
            
            self.output_text.insert(tk.END, f"✓ Parsed schematic\n✓ Found {len(components)} components\n\n")
            self.root.update()
            
            # Save netlist
            if self.netlist_var.get():
                netlist_path = os.path.join(output_dir, f"{base_name}_netlist.txt")
                converter.save_netlist(netlist_path)
                self.output_text.insert(tk.END, f"✓ Netlist saved: {base_name}_netlist.txt\n\n")
                self.output_text.insert(tk.END, "Netlist:\n" + "="*50 + "\n")
                self.output_text.insert(tk.END, netlist + "\n")
                self.root.update()
            
            # Generate diagrams using Lcapy
            if self.svg_var.get() or self.png_var.get():
                self.output_text.insert(tk.END, "\nGenerating diagrams with Lcapy...\n")
                self.root.update()
                
                try:
                    cct = Circuit(netlist)
                    
                    if self.svg_var.get():
                        svg_path = os.path.join(output_dir, f"{base_name}_diagram.svg")
                        try:
                            cct.draw(svg_path)
                            self.output_text.insert(tk.END, f"✓ SVG saved: {base_name}_diagram.svg\n")
                        except Exception as e:
                            self.output_text.insert(tk.END, f"⚠ SVG generation skipped\n")
                        self.root.update()
                    
                    if self.png_var.get():
                        png_path = os.path.join(output_dir, f"{base_name}_diagram.png")
                        try:
                            cct.draw(png_path)
                            self.output_text.insert(tk.END, f"✓ PNG saved: {base_name}_diagram.png\n")
                        except Exception as e:
                            self.output_text.insert(tk.END, f"⚠ PNG generation skipped\n")
                        self.root.update()
                
                except Exception as e:
                    self.output_text.insert(tk.END, f"⚠ Diagram generation note: Lcapy needs LaTeX for full diagram support\n")
                    self.root.update()
            
            self.output_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.output_text.insert(tk.END, "✓ CONVERSION COMPLETE!\n")
            self.output_text.insert(tk.END, f"Output saved to: {output_dir}\n")
            self.status_var.set("Conversion complete!")
            
            messagebox.showinfo("Success", f"Conversion complete!\n\nOutput saved to:\n{output_dir}")
        
        except Exception as e:
            self.output_text.insert(tk.END, f"\n✗ ERROR: {str(e)}\n")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.convert_btn.config(state="normal")


def main():
    root = tk.Tk()
    app = KiCADConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
