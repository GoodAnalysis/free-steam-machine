#Requires -Version 5
<#
.SYNOPSIS
    Install controller-bigpicture as a silent login task.
.DESCRIPTION
    Creates a shortcut in your Startup folder that runs the watcher with
    pythonw.exe (no console window) each time you sign in.
#>

$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$watcher   = Join-Path $scriptDir 'controller_bigpicture.py'

if (-not (Test-Path $watcher)) {
    throw "Cannot find controller_bigpicture.py next to this installer ($scriptDir)."
}

$pythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
if (-not $pythonw) {
    throw "pythonw.exe not found on PATH. Install Python for Windows from python.org with 'Add to PATH' checked."
}

$startup = [Environment]::GetFolderPath('Startup')
$lnkPath = Join-Path $startup 'Controller Big Picture.lnk'

$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath       = $pythonw
$lnk.Arguments        = '"{0}"' -f $watcher
$lnk.WorkingDirectory = $scriptDir
$lnk.Description      = 'Open Steam Big Picture when an Xbox controller connects'
$lnk.Save()

Write-Host "Installed startup entry:" -ForegroundColor Green
Write-Host "  $lnkPath"
Write-Host ""
Write-Host "It will run automatically next time you sign in." -ForegroundColor Green
Write-Host "To start it now without rebooting, run:" -ForegroundColor Green
Write-Host "  Start-Process -FilePath '$pythonw' -ArgumentList '`"$watcher`"'"
