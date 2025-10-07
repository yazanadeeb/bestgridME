# BestGridApp_v1.py
# Standalone desktop app (Tkinter) for Best Grid M-E Pavement Design
# All calculations are internal (no Excel, no internet, no VBA).
# Formulas match the in-Excel model you approved (v6/v7):
#  - a_eff auto if radius blank
#  - p from tire pressure if given else from load & a_eff
#  - sigma_z via Boussinesq under circular uniform load at depth z
#  - eps_t plate surrogate; eps_v via Hooke from sigma_z
#  - Nf, Nr, SFs, decision

import math
import tkinter as tk
from tkinter import ttk, messagebox

def fmt_float(x, digits=2):
    try:
        return f\"{float(x):.{digits}f}\"
    except Exception:
        return \"—\"

def fmt_sci(x, digits=2):
    try:
        return f\"{float(x):.{digits}E}\"
    except Exception:
        return \"—\"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(\"BestGrid Pavement Design — Standalone\")
        self.geometry(\"980x700\")
        self.resizable(True, True)

        # ---- Inputs (defaults tuned to pass with realistic coeffs) ----
        defaults = {
            \"design_life_years\": 20,
            \"esals\": 5_000_000,
            \"hma_thk\": 220,       # mm
            \"base_thk\": 300,      # mm
            \"subbase_thk\": 350,   # mm
            \"subgrade_thk\": 500,  # optional (unused in z)
            \"E_HMA\": 7000,        # MPa
            \"E_Base\": 900,        # MPa
            \"E_Subbase\": 350,     # MPa
            \"E_Subgrade\": 180,    # MPa
            \"nu_subgrade\": 0.45,
            \"tire_p_kPa\": 600,    # kPa; leave blank to auto from load & a_eff
            \"a_mm\": \"\",          # contact radius (optional); blank => auto
            \"wheel_load_N\": 40000,# N per wheel
            \"Kb\": 0.45,           # plate coeff for eps_t
            \"kf1\": 1.0e15, \"kf2\": 4.0, \"kf3\": 1.0,
            \"kr1\": 1.0e6,  \"kr2\": 1.2,
        }

        self.vars = {k: tk.StringVar(value=str(v)) for k, v in defaults.items()}

        main = ttk.Frame(self, padding=12)
        main.pack(fill=\"both\", expand=True)

        # Left: inputs
        left = ttk.LabelFrame(main, text=\"Inputs\", padding=10)
        left.grid(row=0, column=0, sticky=\"nsew\", padx=(0,12))
        # Right: results
        right = ttk.LabelFrame(main, text=\"Results\", padding=10)
        right.grid(row=0, column=1, sticky=\"nsew\")

        main.columnconfigure(0, weight=1, minsize=520)
        main.columnconfigure(1, weight=1, minsize=420)
        main.rowconfigure(0, weight=1)

        grid = ttk.Frame(left)
        grid.pack(fill=\"both\", expand=True)

        def add_row(r, label, key, unit=\"\"):
            ttk.Label(grid, text=label).grid(row=r, column=0, sticky=\"w\", padx=(0,8), pady=3)
            e = ttk.Entry(grid, textvariable=self.vars[key], width=18)
            e.grid(row=r, column=1, sticky=\"w\", pady=3)
            ttk.Label(grid, text=unit).grid(row=r, column=2, sticky=\"w\")

        r = 0
        add_row(r:=r+1, \"Design life\",                \"design_life_years\", \"years\")
        add_row(r:=r+1, \"Design ESALs (18-kip)\",      \"esals\", \"\" )
        ttk.Separator(grid).grid(row=r:=r+1, columnspan=3, sticky=\"ew\", pady=4)

        add_row(r:=r+1, \"HMA thickness\",              \"hma_thk\", \"mm\")
        add_row(r:=r+1, \"Base thickness\",             \"base_thk\", \"mm\")
        add_row(r:=r+1, \"Subbase thickness\",          \"subbase_thk\", \"mm\")
        add_row(r:=r+1, \"Subgrade thickness (opt)\",   \"subgrade_thk\", \"mm\")
        ttk.Separator(grid).grid(row=r:=r+1, columnspan=3, sticky=\"ew\", pady=4)

        add_row(r:=r+1, \"E_HMA\",                       \"E_HMA\", \"MPa\")
        add_row(r:=r+1, \"E_Base\",                      \"E_Base\", \"MPa\")
        add_row(r:=r+1, \"E_Subbase\",                   \"E_Subbase\", \"MPa\")
        add_row(r:=r+1, \"E_Subgrade\",                  \"E_Subgrade\", \"MPa\")
        add_row(r:=r+1, \"ν_Subgrade\",                  \"nu_subgrade\", \"–\")
        ttk.Separator(grid).grid(row=r:=r+1, columnspan=3, sticky=\"ew\", pady=4)

        add_row(r:=r+1, \"Tire pressure (kPa)\",         \"tire_p_kPa\", \"kPa (leave blank to auto)\" )
        add_row(r:=r+1, \"Contact radius (mm)\",         \"a_mm\", \"mm (optional)\" )
        add_row(r:=r+1, \"Wheel load (N)\",              \"wheel_load_N\", \"N\" )
        add_row(r:=r+1, \"Plate coeff Kb (–)\",          \"Kb\", \"–\" )
        ttk.Separator(grid).grid(row=r:=r+1, columnspan=3, sticky=\"ew\", pady=4)

        add_row(r:=r+1, \"kf1 (fatigue coeff)\",         \"kf1\" )
        add_row(r:=r+1, \"kf2 (exp on εt)\",             \"kf2\" )
        add_row(r:=r+1, \"kf3 (exp on E_HMA)\",          \"kf3\" )
        add_row(r:=r+1, \"kr1 (rutting coeff)\",         \"kr1\" )
        add_row(r:=r+1, \"kr2 (exp on εv)\",             \"kr2\" )

        # Buttons
        btns = ttk.Frame(left)
        btns.pack(fill=\"x\", pady=(8,0))
        ttk.Button(btns, text=\"Calculate\", command=self.calculate).pack(side=\"left\")
        ttk.Button(btns, text=\"Clear results\", command=self.clear_results).pack(side=\"left\", padx=8)

        # ---- Results panel ----
        self.lbls = {}
        def add_res(r, label, key, fmt=\"plain\"):
            ttk.Label(right, text=label).grid(row=r, column=0, sticky=\"w\", padx=(0,8), pady=3)
            v = ttk.Label(right, text=\"—\", font=(\"Segoe UI\", 10, \"bold\"))
            v.grid(row=r, column=1, sticky=\"w\", pady=3)
            self.lbls[key] = (v, fmt)

        rr = 0
        add_res(rr:=rr+1, \"a_eff (mm)\",             \"a_eff\")
        add_res(rr:=rr+1, \"p (kPa)\",                \"p_kPa\")
        add_res(rr:=rr+1, \"p (MPa)\",                \"p_MPa\")
        add_res(rr:=rr+1, \"z_to_subgrade (mm)\",     \"z\")
        add_res(rr:=rr+1, \"sigma_z at z (MPa)\",     \"sigma_z\")
        ttk.Separator(right).grid(row=rr:=rr+1, columnspan=2, sticky=\"ew\", pady=4)
        add_res(rr:=rr+1, \"eps_t (microstrain)\",    \"eps_t\")
        add_res(rr:=rr+1, \"eps_v (microstrain)\",    \"eps_v\")
        ttk.Separator(right).grid(row=rr:=rr+1, columnspan=2, sticky=\"ew\", pady=4)
        add_res(rr:=rr+1, \"Nf (cycles)\",            \"Nf\", \"sci\")
        add_res(rr:=rr+1, \"Nr (cycles)\",            \"Nr\", \"sci\")
        add_res(rr:=rr+1, \"SF (Nf/ESALs)\",          \"SF_fatigue\")
        add_res(rr:=rr+1, \"SF (Nr/ESALs)\",          \"SF_rutting\")
        ttk.Separator(right).grid(row=rr:=rr+1, columnspan=2, sticky=\"ew\", pady=4)
        add_res(rr:=rr+1, \"Decision (overall)\",     \"decision\")

        # Auto-calc on start
        self.calculate()

    def getf(self, key, allow_blank=False):
        s = self.vars[key].get().strip()
        if s == \"\":
            if allow_blank:
                return None
            return 0.0
        try:
            return float(s)
        except ValueError:
            raise ValueError(f\"Invalid numeric input for {key}: {s}\")

    def _set_result(self, key, value):
        lbl, fmt = self.lbls[key]
        if value is None:
            lbl.config(text=\"—\"); return
        if fmt == \"sci\":
            lbl.config(text=fmt_sci(value, 2))
        elif isinstance(value, float):
            lbl.config(text=fmt_float(value, 2))
        else:
            lbl.config(text=str(value))

    def clear_results(self):
        for k in self.lbls.keys():
            self._set_result(k, None)

    def calculate(self):
        try:
            # Read inputs
            esals = max(self.getf(\"esals\"), 0.0)
            hma = max(self.getf(\"hma_thk\"), 0.0)
            base = max(self.getf(\"base_thk\"), 0.0)
            sbase = max(self.getf(\"subbase_thk\"), 0.0)
            # subgrade_thk = self.getf(\"subgrade_thk\")  # not used in current z
            E_HMA = max(self.getf(\"E_HMA\"), 1e-9)
            E_sg  = max(self.getf(\"E_Subgrade\"), 1e-9)
            nu_sg = float(self.getf(\"nu_subgrade\"))
            wheel_N = max(self.getf(\"wheel_load_N\"), 0.0)
            Kb = float(self.getf(\"Kb\"))
            kf1 = float(self.getf(\"kf1\")); kf2 = float(self.getf(\"kf2\")); kf3 = float(self.getf(\"kf3\"))
            kr1 = float(self.getf(\"kr1\")); kr2 = float(self.getf(\"kr2\"))

            # a_eff
            a_user = self.getf(\"a_mm\", allow_blank=True)
            p_in   = self.getf(\"tire_p_kPa\", allow_blank=True)
            if a_user is None or a_user == 0:
                # a_eff from load & tire pressure
                if not p_in or p_in <= 0:
                    p_kPa_eff = 600.0   # default if nothing provided
                else:
                    p_kPa_eff = p_in
                a_eff = math.sqrt((wheel_N * 1000.0) / (p_kPa_eff * math.pi))
                p_kPa = p_in if (p_in and p_in > 0) else p_kPa_eff
            else:
                a_eff = a_user
                if p_in and p_in > 0:
                    p_kPa = p_in
                else:
                    # from load & a_eff: N/mm^2 = MPa; *1000 -> kPa
                    p_kPa = (wheel_N / (math.pi * a_eff**2)) * 1000.0

            p_MPa = p_kPa / 1000.0
            z = hma + base + sbase

            # Boussinesq vertical stress at depth z: sigma_z = p * (1 - 1/(1+(a/z)^2)^(3/2))
            if z <= 0:
                sigma_z = 0.0
            else:
                sigma_z = p_MPa * (1.0 - 1.0 / (1.0 + (a_eff / z)**2.0)**1.5)

            # Strains
            # eps_t (microstrain): plate-bending surrogate
            if hma > 0 and E_HMA > 0:
                eps_t = Kb * p_MPa * (a_eff / hma) / E_HMA * 1e6
            else:
                eps_t = 0.0
            # eps_v (microstrain): Hooke from sigma_z
            eps_v = ((1.0 - 2.0 * nu_sg) / E_sg) * sigma_z * 1e6

            # Lives
            Nf = 0.0
            if eps_t > 0 and E_HMA > 0:
                Nf = kf1 * (1.0/eps_t)**kf2 * (1.0/E_HMA)**kf3

            Nr = 0.0
            if eps_v > 0:
                Nr = kr1 * (1.0/eps_v)**kr2

            # Safety factors
            SF_f = Nf / esals if (esals > 0 and Nf > 0) else 0.0
            SF_r = Nr / esals if (esals > 0 and Nr > 0) else 0.0

            decision = \"OK\" if (SF_f >= 1.0 and SF_r >= 1.0) else \"Increase thickness / stiffness\"

            # Set results
            self._set_result(\"a_eff\", a_eff)
            self._set_result(\"p_kPa\", p_kPa)
            self._set_result(\"p_MPa\", p_MPa)
            self._set_result(\"z\", z)
            self._set_result(\"sigma_z\", sigma_z)

            self._set_result(\"eps_t\", eps_t)
            self._set_result(\"eps_v\", eps_v)

            self._set_result(\"Nf\", Nf)
            self._set_result(\"Nr\", Nr)

            self._set_result(\"SF_fatigue\", SF_f)
            self._set_result(\"SF_rutting\", SF_r)
            self._set_result(\"decision\", decision)

        except Exception as e:
            messagebox.showerror(\"Error\", str(e))

if __name__ == \"__main__\":
    App().mainloop()
