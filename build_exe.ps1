$ErrorActionPreference = 'Stop'

pyinstaller --noconfirm --clean --onefile --windowed --name SystemDetails system_details.py
Write-Host "Built dist\SystemDetails.exe"