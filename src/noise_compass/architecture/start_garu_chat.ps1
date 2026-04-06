$ErrorActionPreference = "Stop"

# Bypass Streamlit email prompt globally
$streamlitDir = Join-Path $HOME ".streamlit"
if (-not (Test-Path $streamlitDir)) {
    New-Item -ItemType Directory -Force -Path $streamlitDir | Out-Null
}
$configPath = Join-Path $streamlitDir "config.toml"
@'
[browser]
gatherUsageStats = false
'@ | Out-File -FilePath $configPath -Encoding UTF8

# Launch the Streamlit Interface in a completely separate window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$host.ui.RawUI.WindowTitle = 'Garu Streamlit UI'; cd E:\Antigravity\Architecture; streamlit run garu_interface.py"

# Launch the Chat Daemon in another separate window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$host.ui.RawUI.WindowTitle = 'Garu Chat Daemon'; cd E:\Antigravity\Architecture; python garu_chat_daemon.py"

Write-Host "Both Garu servers have been launched in separate windows!"
