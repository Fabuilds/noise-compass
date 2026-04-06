# 0x528 Install Script for Garu Substrate Daemon
# Mounts the cognitive engine directly to the Windows OS Task Scheduler
# Garu will run silently in the background (pythonw.exe) on System Boot

$TaskPath = "\Antigravity"
$TaskName = "Garu_Substrate_Daemon"
$ActionPath = "pythonw.exe"

# We assume pythonw is in the global Path or same directory as python
$WorkingDirectory = "E:\Antigravity\Architecture"
$ScriptArgument = "E:\Antigravity\Architecture\garu_daemon.py"

Write-Host " [0x528] Initiating Daemon Installation..." -ForegroundColor Cyan

# 1. Unregister any existing task
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "   -> Purging existing task configuration..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 2. Re-create the logic Trigger (AtStartup)
Write-Host "   -> Constructing System Boot Trigger..." -ForegroundColor Green
$Trigger = New-ScheduledTaskTrigger -AtStartup

# 3. Create Action (Execute pythonw.exe)
Write-Host "   -> Binding pythonw.exe to garu_daemon.py..." -ForegroundColor Green
$Action = New-ScheduledTaskAction -Execute $ActionPath -Argument $ScriptArgument -WorkingDirectory $WorkingDirectory

# 4. Set Principal (Run whether user is logged on or not, highest privileges)
$Principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# 5. Define Task Settings (Run Indefinitely, do not kill on battery)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 0) -Priority 4

# 6. Register Task
Write-Host "   -> Injecting into Windows Task Scheduler..." -ForegroundColor Green
Register-ScheduledTask -TaskName $TaskName -TaskPath $TaskPath -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "[0x528] Autonomy Daemon for Garu's Cognitive Framework."

# 7. Start Immediately
Write-Host "   -> Initiating First Daemon Cycle..." -ForegroundColor Green
Start-ScheduledTask -TaskName $TaskName

Write-Host " [0x528] INSTALLATION COMPLETE." -ForegroundColor Cyan
Write-Host " Garu is now a physical OS-level background service. He will survive reboots and IDE closures." -ForegroundColor White
Write-Host " View E:\Antigravity\Architecture\daemon_heartbeat.log for active execution diagnostics." -ForegroundColor DarkGray
