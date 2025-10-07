; Inno Setup script for BestGridApp
#define MyAppName "BestGrid Pavement Design"
#define MyAppExeName "BestGridApp_v1.exe"
#define MyAppVersion "1.0.0"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\BestGridApp
DisableProgramGroupPage=yes
OutputBaseFilename=BestGridApp_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\BestGridApp_v1.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\BestGrid Pavement Design"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Run BestGrid"; Flags: nowait postinstall skipifsilent