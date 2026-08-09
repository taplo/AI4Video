# install-hooks.ps1 - Install git hooks for harness verification
# Run this once per repository to set up pre-commit hooks

param(
    [switch]$Force
)

$hookPath = ".git/hooks/pre-commit"
$hookContent = @'
#!/bin/sh
# Harness pre-commit hook
# Runs verification before allowing commit

echo "=== Running pre-commit verification ==="

# Detect project type and run checks
if [ -f "package.json" ]; then
    echo "Running npm checks..."
    npm run typecheck 2>&1 && npm run lint 2>&1
elif [ -f "pyproject.toml" ]; then
    echo "Running uv checks..."
    ruff check . 2>&1 && mypy . 2>&1
elif [ -f "Cargo.toml" ]; then
    echo "Running cargo checks..."
    cargo check 2>&1
elif [ -f "CMakeLists.txt" ]; then
    echo "Running cmake checks..."
    cmake --build build 2>&1
elif [ -f "go.mod" ]; then
    echo "Running go checks..."
    go vet ./... 2>&1
fi

exit $?
'@

# For Windows PowerShell environments, also create a .ps1 version
$psHookContent = @'
# Harness pre-commit hook (PowerShell)
# Runs verification before allowing commit

Write-Host "=== Running pre-commit verification ===" -ForegroundColor Cyan

if (Test-Path "package.json") {
    Write-Host "Running npm checks..."
    & npm run typecheck 2>&1
    if ($LASTEXITCODE -ne 0) { exit 1 }
    & npm run lint 2>&1
    exit $LASTEXITCODE
}
elseif (Test-Path "pyproject.toml") {
    Write-Host "Running uv checks..."
    & ruff check . 2>&1
    if ($LASTEXITCODE -ne 0) { exit 1 }
    & mypy . 2>&1
    exit $LASTEXITCODE
}
elseif (Test-Path "Cargo.toml") {
    Write-Host "Running cargo checks..."
    & cargo check 2>&1
    exit $LASTEXITCODE
}
elseif (Test-Path "go.mod") {
    Write-Host "Running go checks..."
    & go vet ./...
    exit $LASTEXITCODE
}
'@

if (-not (Test-Path ".git")) {
    Write-Host "Error: Not a git repository" -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Path ".git/hooks" -Force | Out-Null

# Write shell hook (for git bash / WSL)
$hookContent | Set-Content -Path $hookPath -NoNewline
# Write PowerShell hook
$psHookContent | Set-Content -Path ".git/hooks/pre-commit.ps1" -NoNewline

# Make executable on Unix-like systems
if ($IsLinux -or $IsMacOS) {
    chmod +x $hookPath
}

Write-Host "Hooks installed successfully!" -ForegroundColor Green
Write-Host "Pre-commit will now run verification checks before each commit."
