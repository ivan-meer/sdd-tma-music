# PowerShell wrapper to run the CSV->GitHub Issues importer
# Usage: powershell -ExecutionPolicy Bypass -File .\.github\issue-import\run_import.ps1

param(
    [string]$Repo = '',
    [string]$Csv = '.github/issue-import/tasks_issues.csv',
    [int]$Sleep = 0.5
)

function Read-Token {
    if ($env:GITHUB_TOKEN) {
        return $env:GITHUB_TOKEN
    }
    Write-Host "GITHUB_TOKEN not found in environment. Please paste your Personal Access Token (it will not be stored):"
    $sec = Read-Host -AsSecureString "GitHub token"
    try {
        $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
        $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
        return $plain
    } catch {
        Write-Error "Failed to read token. Please set GITHUB_TOKEN environment variable and retry."
        exit 1
    }
}

# Validate CSV exists
$csvPath = Join-Path (Get-Location) $Csv
if (-not (Test-Path $csvPath)) {
    Write-Error "CSV file not found: $csvPath"
    exit 1
}

# Ask repo if not provided
if (-not $Repo) {
    $Repo = Read-Host "Enter GitHub repo (owner/repo) to import issues into"
}

$token = Read-Token
if (-not $token) { Write-Error "No token provided"; exit 1 }

# Export token for child process
$orig = $env:GITHUB_TOKEN
$env:GITHUB_TOKEN = $token

# Dry-run
Write-Host "Running dry-run (no issues will be created)..."
$dryCmd = "python ./.github/issue-import/import_issues.py --repo $Repo --csv $Csv --dry-run --sleep $Sleep"
Write-Host "Command: $dryCmd"
$dryExit = & python .\.github\issue-import\import_issues.py --repo $Repo --csv $Csv --dry-run --sleep $Sleep
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Dry-run returned non-zero exit code. Inspect output above for errors. Common causes: wrong repo, insufficient token scopes, network issues, missing milestones."
}

# Confirm proceed
$confirm = Read-Host "Proceed to create issues? Type 'yes' to continue"
if ($confirm -ne 'yes') {
    Write-Host "Aborted by user. No changes made."
    if ($null -ne $orig) { $env:GITHUB_TOKEN = $orig } else { Remove-Item Env:\GITHUB_TOKEN -ErrorAction SilentlyContinue }
    exit 0
}

# Create issues
Write-Host "Creating issues..."
& python .\.github\issue-import\import_issues.py --repo $Repo --csv $Csv --sleep $Sleep
if ($LASTEXITCODE -ne 0) {
    Write-Error "Import script failed. See output above for details."
} else {
    Write-Host "Import completed. Check repository issues for created items."
}

# Restore env
if ($null -ne $orig) { $env:GITHUB_TOKEN = $orig } else { Remove-Item Env:\GITHUB_TOKEN -ErrorAction SilentlyContinue }

Write-Host "Done."