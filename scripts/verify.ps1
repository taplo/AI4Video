# verify.ps1 - Harness verification script
# Auto-detects project type and runs appropriate checks

param(
    [switch]$Quiet,
    [string]$ProjectPath = "."
)

$ErrorActionPreference = "Stop"
$exitCode = 0

function Write-CheckHeader($name) {
    if (-not $Quiet) { Write-Host "`n=== $name ===" -ForegroundColor Cyan }
}

function Write-Pass($msg) {
    if (-not $Quiet) { Write-Host "  PASS: $msg" -ForegroundColor Green }
}

function Write-Fail($msg) {
    Write-Host "  FAIL: $msg" -ForegroundColor Red
    $script:exitCode = 1
}

function Write-Skip($msg) {
    if (-not $Quiet) { Write-Host "  SKIP: $msg" -ForegroundColor Yellow }
}

# Detect project type
$projectFiles = Get-ChildItem -Path $ProjectPath -File
$hasPackageJson = $projectFiles | Where-Object { $_.Name -eq "package.json" }
$hasPyproject = $projectFiles | Where-Object { $_.Name -eq "pyproject.toml" }
$hasCargo = $projectFiles | Where-Object { $_.Name -eq "Cargo.toml" }
$hasCMake = $projectFiles | Where-Object { $_.Name -eq "CMakeLists.txt" }
$hasGoMod = $projectFiles | Where-Object { $_.Name -eq "go.mod" }

# --- JavaScript / TypeScript ---
if ($hasPackageJson) {
    Write-CheckHeader "JavaScript/TypeScript Checks"

    # Check for package manager
    $pm = "npm"
    if (Test-Path "pnpm-lock.yaml") { $pm = "pnpm" }
    elseif (Test-Path "yarn.lock") { $pm = "yarn" }
    elseif (Test-Path "bun.lockb") { $pm = "bun" }

    $pkgJson = Get-Content "package.json" | ConvertFrom-Json

    # Type check
    if ($pkgJson.scripts.typecheck) {
        Write-Host "  Running typecheck..."
        & $pm run typecheck 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "typecheck" } else { Write-Fail "typecheck (exit $LASTEXITCODE)" }
    } else {
        Write-Skip "typecheck (no script defined)"
    }

    # Lint
    if ($pkgJson.scripts.lint) {
        Write-Host "  Running lint..."
        & $pm run lint 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "lint" } else { Write-Fail "lint (exit $LASTEXITCODE)" }
    } else {
        Write-Skip "lint (no script defined)"
    }

    # Test
    if ($pkgJson.scripts.test) {
        Write-Host "  Running tests..."
        & $pm test 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "tests" } else { Write-Fail "tests (exit $LASTEXITCODE)" }
    } else {
        Write-Skip "tests (no script defined)"
    }
}

# --- Python / Django ---
elseif ($hasPyproject -or (Test-Path "manage.py")) {
    Write-CheckHeader "Python/Django Checks"

    # Use uv if available
    $uvPath = "C:\Users\Administrator\.local\bin\uv.exe"
    if (-not (Test-Path $uvPath)) {
        $uvPath = "uv"
    }

    # Syntax check (py_compile)
    Write-Host "  Running Python syntax check..."
    $pyFiles = Get-ChildItem -Path $ProjectPath -Filter "*.py" -Recurse | Where-Object { $_.FullName -notlike "*\migrations\*" -and $_.FullName -notlike "*\__pycache__\*" }
    $syntaxErrors = 0
    foreach ($file in $pyFiles) {
        & $uvPath run python -m py_compile $file.FullName 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "    SYNTAX ERROR: $($file.Name)" -ForegroundColor Red
            $syntaxErrors++
        }
    }
    if ($syntaxErrors -eq 0) { Write-Pass "Python syntax" } else { Write-Fail "Python syntax ($syntaxErrors files)" }

    # Django system check
    if (Test-Path "manage.py") {
        Write-Host "  Running Django system check..."
        & $uvPath run python manage.py check --deploy 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "Django check" } else { Write-Fail "Django check (exit $LASTEXITCODE)" }
    }

    # Type check (mypy)
    if (Get-Command mypy -ErrorAction SilentlyContinue) {
        Write-Host "  Running mypy..."
        & $uvPath run mypy . 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "mypy" } else { Write-Fail "mypy (exit $LASTEXITCODE)" }
    } else {
        Write-Skip "mypy (not installed)"
    }

    # Lint (ruff)
    if (Get-Command ruff -ErrorAction SilentlyContinue) {
        Write-Host "  Running ruff..."
        & $uvPath run ruff check . 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "ruff" } else { Write-Fail "ruff (exit $LASTEXITCODE)" }
    } else {
        Write-Skip "ruff (not installed)"
    }

    # Test (pytest or Django test)
    if (Test-Path "tests" -PathType Container) {
        Write-Host "  Running pytest..."
        & $uvPath run pytest tests/ --cov=app --cov-fail-under=29 -v 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "pytest" } else { Write-Fail "pytest (exit $LASTEXITCODE)" }
    } elseif (Test-Path "manage.py") {
        Write-Host "  Running Django tests..."
        & $uvPath run python manage.py test app.tests --verbosity=2 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "Django tests" } else { Write-Fail "Django tests (exit $LASTEXITCODE)" }
    } else {
        Write-Skip "No tests found"
    }
}

# --- C++ (CMake) ---
elseif ($hasCMake) {
    Write-CheckHeader "C++ Checks"

    # Build
    if (Test-Path "build" -PathType Container) {
        Write-Host "  Running cmake build..."
        cmake --build build --config Release 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "cmake build" } else { Write-Fail "cmake build (exit $LASTEXITCODE)" }

        # CTest
        Write-Host "  Running ctest..."
        ctest --test-dir build --output-on-failure 2>&1
        if ($LASTEXITCODE -eq 0) { Write-Pass "ctest" } else { Write-Fail "ctest (exit $LASTEXITCODE)" }
    } else {
        Write-Skip "cmake build (no build/ directory)"
    }
}

# --- Rust ---
elseif ($hasCargo) {
    Write-CheckHeader "Rust Checks"

    Write-Host "  Running cargo check..."
    cargo check 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Pass "cargo check" } else { Write-Fail "cargo check (exit $LASTEXITCODE)" }

    Write-Host "  Running clippy..."
    cargo clippy -- -D warnings 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Pass "clippy" } else { Write-Fail "clippy (exit $LASTEXITCODE)" }

    Write-Host "  Running cargo test..."
    cargo test 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Pass "cargo test" } else { Write-Fail "cargo test (exit $LASTEXITCODE)" }
}

# --- Go ---
elseif ($hasGoMod) {
    Write-CheckHeader "Go Checks"

    Write-Host "  Running go vet..."
    go vet ./... 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Pass "go vet" } else { Write-Fail "go vet (exit $LASTEXITCODE)" }

    Write-Host "  Running go test..."
    go test ./... 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Pass "go test" } else { Write-Fail "go test (exit $LASTEXITCODE)" }
}

else {
    Write-Skip "No recognized project type detected"
}

# --- Summary ---
if (-not $Quiet) {
    Write-Host "`n=== Summary ===" -ForegroundColor Cyan
    if ($exitCode -eq 0) {
        Write-Host "All checks passed!" -ForegroundColor Green
    } else {
        Write-Host "Some checks failed." -ForegroundColor Red
    }
}

exit $exitCode
