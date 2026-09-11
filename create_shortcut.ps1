$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "AI Resume & Portfolio Agent.lnk"
$TargetFolder = "C:\Users\ADMIN\Desktop\Resume portfolio ai agent"
$TargetFile = Join-Path $TargetFolder "LAUNCH_AGENT.bat"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = $TargetFolder
$Shortcut.Description = "Launch AI Resume and Portfolio Builder Dashboard"
$Shortcut.IconLocation = "shell32.dll,220"
$Shortcut.Save()

Write-Host "`n[SUCCESS] Desktop Shortcut created successfully at:" -ForegroundColor Green
Write-Host " -> $ShortcutPath" -ForegroundColor Cyan
Write-Host "You can now launch your AI agent from your Desktop anytime!`n" -ForegroundColor Yellow
