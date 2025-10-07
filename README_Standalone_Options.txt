BestGrid — 100% Standalone EXE without installing Python on your PC
===================================================================

This folder contains:
- BestGridApp_v1.py
- .github/workflows/build.yml      (GitHub Actions workflow to build EXE in the cloud)
- installer.iss                    (Inno Setup script to create a Windows installer from the EXE)

Two ways to get a standalone EXE without installing Python locally:

Option A — GitHub Actions (recommended)
--------------------------------------
1) Create a new GitHub repo and push these three files (and BestGridApp_v1.py) to it.
2) Go to the "Actions" tab in GitHub, enable workflows if prompted.
3) Run the workflow "Build BestGrid EXE" (Actions → Workflows → Build BestGrid EXE → Run workflow).
4) When it finishes, download the artifact "BestGridApp_Windows_EXE" — it contains BestGridApp_v1.exe.
   This EXE runs on Windows WITHOUT Python installed.

Option B — Local build (if you have Python once)
------------------------------------------------
1) Install Python 3.10+ locally, then run:
   pip install pyinstaller
   pyinstaller --onefile --noconsole --name BestGridApp_v1 BestGridApp_v1.py
2) You will get dist/BestGridApp_v1.exe — it runs on any Windows machine without Python.

Optional: Create a Windows Installer (Setup.exe)
------------------------------------------------
1) Install "Inno Setup" (free). Open installer.iss in Inno Setup.
2) Build → Compile. It will package your EXE into BestGridApp_Setup.exe (nice installer).

Notes
-----
- No Excel / No VBA / No Internet required by the app.
- Formulas match your approved Excel model (v7):
  * a_eff auto if contact radius blank
  * p from tire pressure if given else from load & a_eff
  * sigma_z via Boussinesq at depth z = HMA+Base+Subbase
  * eps_t plate surrogate; eps_v from sigma_z
  * Nf, Nr, SFs, decision