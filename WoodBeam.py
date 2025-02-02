import tkinter as tk
from tkinter import ttk, messagebox
import math

class WoodBeamCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Wood Beam Calculator (2024 NDS)")
        self.root.geometry("600x800")
        
        # Wood species and grades data
        self.wood_data = {
            "Southern Pine-No.1": {
                "Fb": 2600,  # psi (Bending)
                "E": 1600000,  # psi (Modulus of Elasticity)
                "Cd": 1.0,    # Load Duration Factor
                "Cm": 1.0,    # Wet Service Factor
                "Ct": 1.0,    # Temperature Factor
                "CL": 1.0,    # Beam Stability Factor
                "CF": 1.0,    # Size Factor
                "Ci": 1.0,    # Incising Factor
                "Cr": 1.15    # Repetitive Member Factor
            },
            "Douglas Fir-Larch-No.1": {
                "Fb": 2400,
                "E": 1600000,
                "Cd": 1.0,
                "Cm": 1.0,
                "Ct": 1.0,
                "CL": 1.0,
                "CF": 1.0,
                "Ci": 1.0,
                "Cr": 1.15
            }
        }
        
        # Common beam sizes (nominal dimensions in inches)
        self.beam_sizes = [
            "2x6", "2x8", "2x10", "2x12",
            "3x6", "3x8", "3x10", "3x12",
            "4x6", "4x8", "4x10", "4x12"
        ]
        
        self.create_widgets()
    
    def create_widgets(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Input Parameters", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Span Length
        ttk.Label(input_frame, text="Span Length (ft):").grid(row=0, column=0, sticky="w")
        self.span_entry = ttk.Entry(input_frame)
        self.span_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Dead Load
        ttk.Label(input_frame, text="Dead Load (psf):").grid(row=1, column=0, sticky="w")
        self.dead_load_entry = ttk.Entry(input_frame)
        self.dead_load_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Live Load
        ttk.Label(input_frame, text="Live Load (psf):").grid(row=2, column=0, sticky="w")
        self.live_load_entry = ttk.Entry(input_frame)
        self.live_load_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Snow Load
        ttk.Label(input_frame, text="Snow Load (psf):").grid(row=3, column=0, sticky="w")
        self.snow_load_entry = ttk.Entry(input_frame)
        self.snow_load_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Tributary Width
        ttk.Label(input_frame, text="Tributary Width (ft):").grid(row=4, column=0, sticky="w")
        self.trib_width_entry = ttk.Entry(input_frame)
        self.trib_width_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # Wood Species Selection
        ttk.Label(input_frame, text="Wood Species:").grid(row=5, column=0, sticky="w")
        self.species_var = tk.StringVar()
        species_combo = ttk.Combobox(input_frame, textvariable=self.species_var)
        species_combo['values'] = list(self.wood_data.keys())
        species_combo.grid(row=5, column=1, padx=5, pady=5)
        species_combo.set(list(self.wood_data.keys())[0])
        
        # Calculate Button
        ttk.Button(self.root, text="Calculate", command=self.calculate_beam).pack(pady=10)
        
        # Results Frame
        self.results_frame = ttk.LabelFrame(self.root, text="Results", padding="10")
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Results Text
        self.results_text = tk.Text(self.results_frame, height=20, width=60)
        self.results_text.pack(fill="both", expand=True)
        
    def calculate_beam(self):
        try:
            # Get input values
            L = float(self.span_entry.get()) * 12  # Convert to inches
            DL = float(self.dead_load_entry.get())
            LL = float(self.live_load_entry.get())
            SL = float(self.snow_load_entry.get())
            trib_width = float(self.trib_width_entry.get())
            species = self.species_var.get()
            
            # Calculate total load (plf)
            w = (DL + LL + SL) * trib_width
            
            # Maximum moment (in-lbs)
            M_max = (w * L * L) / 8
            
            # Get wood properties
            wood_props = self.wood_data[species]
            
            suitable_beams = []
            
            # Check each beam size
            for size in self.beam_sizes:
                width, height = map(int, size.split('x'))
                # Convert nominal to actual dimensions
                if width <= 2:
                    actual_width = width - 0.5
                else:
                    actual_width = width - 0.75
                actual_height = height - 0.75
                
                # Calculate section properties
                I = (actual_width * actual_height**3) / 12  # Moment of inertia
                S = (actual_width * actual_height**2) / 6   # Section modulus
                
                # Calculate actual stress
                fb_actual = M_max / S
                
                # Calculate allowable stress
                Fb_prime = wood_props["Fb"] * wood_props["Cd"] * wood_props["Cm"] * \
                          wood_props["Ct"] * wood_props["CL"] * wood_props["CF"] * \
                          wood_props["Ci"] * wood_props["Cr"]
                
                # Calculate deflection
                delta = (5 * w * L**4) / (384 * wood_props["E"] * I)
                delta_limit = L/360  # Standard deflection limit
                
                # Check if beam is suitable
                if fb_actual <= Fb_prime and delta <= delta_limit:
                    suitable_beams.append({
                        'size': size,
                        'stress_ratio': fb_actual/Fb_prime * 100,
                        'deflection_ratio': delta/delta_limit * 100
                    })
            
            # Sort beams by stress ratio (most efficient use of material)
            suitable_beams.sort(key=lambda x: x['stress_ratio'], reverse=True)
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            if suitable_beams:
                self.results_text.insert(tk.END, "Suitable Beam Options:\n\n")
                for i, beam in enumerate(suitable_beams[:5], 1):
                    self.results_text.insert(tk.END, 
                        f"{i}. {beam['size']}\n"
                        f"   Stress Utilization: {beam['stress_ratio']:.1f}%\n"
                        f"   Deflection Utilization: {beam['deflection_ratio']:.1f}%\n\n"
                    )
            else:
                self.results_text.insert(tk.END, "No suitable beams found. Consider:\n"
                                               "1. Reducing span length\n"
                                               "2. Using a different wood species\n"
                                               "3. Using multiple beams\n"
                                               "4. Using a different material\n")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for all fields.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WoodBeamCalculator(root)
    root.mainloop()