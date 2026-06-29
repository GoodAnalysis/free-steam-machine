#Requires -Version 5
<#
.SYNOPSIS
    Remove the controller-bigpicture startup entry.
#>

$ErrorActionPreference = 'Stop'

$startup = [Environment]::GetFolderPath('Startup')
$lnkPath = Join-Path $startup 'Controller Big Picture.lnk'

if (Test-Path $lnkPath) {
    Remove-Item $lnkPath -Force
    Write-Host "Removed startup entry: $lnkPath" -ForegroundColor Green
} else {
    Write-Host "No startup entry found; nothing to remove." -ForegroundColor Yellow
}

Write-Host "If a watcher is currently running, end 'pythonw.exe' in Task Manager to stop it."
