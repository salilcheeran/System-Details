# System Details

A compact Windows desktop dashboard for viewing laptop configuration and live performance.

## Run from Python

```powershell
python system_details.py
```

The application uses Tkinter from the Python standard library, so no runtime package installation is required. It opens at approximately 8 x 5 inches, includes a drawn gear icon in the title area, and keeps the navigation footer fixed while detail content scrolls.

## Build a standalone EXE

PyInstaller is required only on the build machine. From this folder, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

The finished executable is written to `dist\SystemDetails.exe`. Copy that file to another Windows laptop to run the application without installing Python or other packages.

## Controls

- **Configuration** opens a summary of the operating system, processor, memory, storage, Python runtime, and host name.
- **Performance** opens a live panel with CPU, memory, and storage readings.
- **Exit** closes the application.
