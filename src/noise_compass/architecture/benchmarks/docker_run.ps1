# docker_run.ps1 — Antigravity Benchmark Container Manager
# Assists in building the image and executing tests within the sandbox.

param (
    [string]$Action = "build",
    [string]$ExercisePath = "",
    [string]$Command = ""
)

$ImageName = "antigravity-bench"

if ($Action -eq "build") {
    Write-Host "[DOCKER]: Building $ImageName..."
    docker build -t $ImageName .
} 
elseif ($Action -eq "run") {
    if (-not $ExercisePath) {
        Write-Error "[ERROR]: ExercisePath is required for 'run' action."
        return
    }
    
    # Mount the specific exercise directory to /workspace
    # Use absolute path for Windows-Docker compatibility
    $AbsPath = Resolve-Path $ExercisePath
    Write-Host "[DOCKER]: Running tests in $AbsPath..."
    
    docker run --rm -v "${AbsPath}:/workspace" $ImageName /bin/bash -c "$Command"
}
else {
    Write-Error "[ERROR]: Unknown action: $Action. Use 'build' or 'run'."
}
