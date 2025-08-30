# PathRAG with ArangoDB - Windows Development Deployment Script
# This script provides automated setup for PathRAG with ArangoDB on Windows
# Compatible with Windows 10/11 with PowerShell 5.1+

param(
    [switch]$Help,
    [switch]$Version,
    [switch]$Check,
    [switch]$Status,
    [switch]$Install,
    [switch]$Start,
    [switch]$Stop,
    [string]$ArangoPassword = "pathrag123",
    [string]$Port = "5000"
)

# Script configuration
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$LogFile = "$env:TEMP\pathrag_deploy.log"
$AppDir = $ProjectRoot
$ServiceName = "PathRAG"
$VenvPath = "$AppDir\venv"
$PythonExe = "$VenvPath\Scripts\python.exe"
$PipExe = "$VenvPath\Scripts\pip.exe"

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    White = "White"
}

# Logging functions
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Host $LogMessage -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $LogMessage
}

function Write-Success {
    param([string]$Message)
    Write-Log "✓ $Message" -Color $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Log "⚠ $Message" -Color $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Log "✗ $Message" -Color $Colors.Red
}

function Write-Info {
    param([string]$Message)
    Write-Log "ℹ $Message" -Color $Colors.Blue
}

# Error handling
function Exit-WithError {
    param([string]$Message)
    Write-Error $Message
    Write-Error "Deployment failed. Check log file: $LogFile"
    exit 1
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check system requirements
function Test-SystemRequirements {
    Write-Log "Checking system requirements..."
    
    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    if ($osVersion.Major -lt 10) {
        Exit-WithError "Windows 10 or later is required"
    }
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Exit-WithError "PowerShell 5.1 or later is required"
    }
    
    # Check if Chocolatey is available
    $chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $chocoInstalled) {
        Write-Warning "Chocolatey not found. Some installations may require manual intervention."
    }
    
    Write-Success "System requirements check completed"
}

# Install Chocolatey if not present
function Install-Chocolatey {
    $chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $chocoInstalled) {
        Write-Log "Installing Chocolatey..."
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Success "Chocolatey installed"
    } else {
        Write-Info "Chocolatey already installed"
    }
}

# Install Python
function Install-Python {
    Write-Log "Checking Python installation..."
    
    $pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonInstalled) {
        Write-Log "Installing Python..."
        try {
            choco install python -y
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            Write-Success "Python installed"
        } catch {
            Exit-WithError "Failed to install Python: $($_.Exception.Message)"
        }
    } else {
        Write-Info "Python already installed"
    }
    
    # Verify Python version
    try {
        $pythonVersion = python --version 2>&1
        Write-Info "Python version: $pythonVersion"
    } catch {
        Exit-WithError "Python installation verification failed"
    }
}

# Install Git
function Install-Git {
    Write-Log "Checking Git installation..."
    
    $gitInstalled = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitInstalled) {
        Write-Log "Installing Git..."
        try {
            choco install git -y
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            Write-Success "Git installed"
        } catch {
            Exit-WithError "Failed to install Git: $($_.Exception.Message)"
        }
    } else {
        Write-Info "Git already installed"
    }
}

# Install ArangoDB
function Install-ArangoDB {
    Write-Log "Checking ArangoDB installation..."
    
    # Check if ArangoDB is already running
    $arangoProcess = Get-Process -Name "arangod" -ErrorAction SilentlyContinue
    if ($arangoProcess) {
        Write-Info "ArangoDB is already running"
        return
    }
    
    # Check if ArangoDB is installed
    $arangoInstalled = Test-Path "C:\Program Files\ArangoDB3*\bin\arangod.exe"
    if (-not $arangoInstalled) {
        Write-Log "Installing ArangoDB..."
        
        # Download ArangoDB installer
        $arangoUrl = "https://download.arangodb.com/arangodb39/Community/Windows/ArangoDB3-3.9.11_win64.exe"
        $installerPath = "$env:TEMP\ArangoDB_installer.exe"
        
        try {
            Write-Log "Downloading ArangoDB installer..."
            Invoke-WebRequest -Uri $arangoUrl -OutFile $installerPath
            
            Write-Log "Installing ArangoDB (this may take a few minutes)..."
            Start-Process -FilePath $installerPath -ArgumentList "/S", "/PASSWORD=$ArangoPassword" -Wait
            
            Remove-Item $installerPath -Force
            Write-Success "ArangoDB installed"
        } catch {
            Exit-WithError "Failed to install ArangoDB: $($_.Exception.Message)"
        }
    } else {
        Write-Info "ArangoDB already installed"
    }
    
    # Start ArangoDB service
    try {
        $arangoService = Get-Service -Name "ArangoDB" -ErrorAction SilentlyContinue
        if ($arangoService) {
            if ($arangoService.Status -ne "Running") {
                Start-Service -Name "ArangoDB"
                Write-Success "ArangoDB service started"
            } else {
                Write-Info "ArangoDB service already running"
            }
        } else {
            Write-Warning "ArangoDB service not found. You may need to start it manually."
        }
    } catch {
        Write-Warning "Failed to start ArangoDB service: $($_.Exception.Message)"
    }
    
    # Wait for ArangoDB to be ready
    Write-Log "Waiting for ArangoDB to be ready..."
    $maxAttempts = 30
    $attempt = 0
    do {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8529/_api/version" -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "ArangoDB is ready"
                break
            }
        } catch {
            # Continue waiting
        }
        Start-Sleep -Seconds 2
        $attempt++
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        Write-Warning "ArangoDB may not be ready. Please check manually at http://localhost:8529"
    }
}

# Create Python virtual environment
function New-VirtualEnvironment {
    Write-Log "Creating Python virtual environment..."
    
    if (Test-Path $VenvPath) {
        Write-Info "Virtual environment already exists"
        return
    }
    
    try {
        python -m venv $VenvPath
        Write-Success "Virtual environment created"
    } catch {
        Exit-WithError "Failed to create virtual environment: $($_.Exception.Message)"
    }
}

# Install Python dependencies
function Install-PythonDependencies {
    Write-Log "Installing Python dependencies..."
    
    try {
        # Upgrade pip
        & $PipExe install --upgrade pip
        
        # Install requirements if file exists
        $requirementsFile = "$AppDir\requirements.txt"
        if (Test-Path $requirementsFile) {
            & $PipExe install -r $requirementsFile
        } else {
            Write-Warning "requirements.txt not found, installing basic dependencies"
            & $PipExe install flask python-dotenv pyarango requests
        }
        
        Write-Success "Python dependencies installed"
    } catch {
        Exit-WithError "Failed to install Python dependencies: $($_.Exception.Message)"
    }
}

# Configure environment
function Set-Environment {
    Write-Log "Configuring environment..."
    
    # Copy example.env to .env if it doesn't exist
    $envFile = "$AppDir\.env"
    $exampleEnvFile = "$AppDir\example.env"
    
    if (-not (Test-Path $envFile) -and (Test-Path $exampleEnvFile)) {
        Copy-Item $exampleEnvFile $envFile
        Write-Success "Environment file created from example.env"
    } else {
        Write-Warning ".env file already exists or example.env not found"
    }
    
    # Create directories
    $directories = @("logs", "pathrag_data", "backups")
    foreach ($dir in $directories) {
        $dirPath = "$AppDir\$dir"
        if (-not (Test-Path $dirPath)) {
            New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
            Write-Info "Created directory: $dir"
        }
    }
    
    Write-Success "Environment configured"
}

# Test PathRAG setup
function Test-PathRAGSetup {
    Write-Log "Testing PathRAG setup..."
    
    try {
        # Test configuration loading
        $testScript = @"
import sys
sys.path.append('$($AppDir.Replace('\', '\\'))')
sys.path.append('$($AppDir.Replace('\', '\\'))\\src')

try:
    from config import get_config
    config = get_config()
    print('✓ Configuration loaded successfully')
    print(f'ArangoDB: {config.arangodb.connection_url}')
    print(f'Working Directory: {config.pathrag.working_dir}')
except Exception as e:
    print(f'✗ Configuration test failed: {e}')
    exit(1)
"@
        
        $testFile = "$env:TEMP\test_config.py"
        Set-Content -Path $testFile -Value $testScript
        
        $result = & $PythonExe $testFile 2>&1
        Write-Info $result
        
        Remove-Item $testFile -Force
        Write-Success "PathRAG setup test completed"
    } catch {
        Write-Warning "PathRAG setup test failed: $($_.Exception.Message)"
    }
}

# Start PathRAG service
function Start-PathRAGService {
    Write-Log "Starting PathRAG service..."
    
    try {
        # Check if API server script exists
        $apiScript = "$AppDir\scripts\api_server.py"
        if (-not (Test-Path $apiScript)) {
            Write-Warning "API server script not found at $apiScript"
            Write-Info "You can start PathRAG manually using the Python scripts"
            return
        }
        
        # Start the API server in background
        $job = Start-Job -ScriptBlock {
            param($PythonPath, $ScriptPath, $AppPath)
            Set-Location $AppPath
            & $PythonPath $ScriptPath
        } -ArgumentList $PythonExe, $apiScript, $AppDir
        
        Write-Info "PathRAG service started in background (Job ID: $($job.Id))"
        Write-Info "Use 'Get-Job' to check status and 'Stop-Job $($job.Id)' to stop"
        
        # Wait a moment and test if service is responding
        Start-Sleep -Seconds 5
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Success "PathRAG service is responding at http://localhost:$Port"
            }
        } catch {
            Write-Warning "PathRAG service may not be ready yet. Check manually at http://localhost:$Port/health"
        }
        
    } catch {
        Write-Warning "Failed to start PathRAG service: $($_.Exception.Message)"
    }
}

# Run health checks
function Test-HealthChecks {
    Write-Log "Running health checks..."
    
    # Check ArangoDB
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8529/_api/version" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Success "ArangoDB is healthy"
        } else {
            Write-Warning "ArangoDB health check failed"
        }
    } catch {
        Write-Warning "ArangoDB is not responding"
    }
    
    # Check PathRAG service
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Success "PathRAG service is healthy"
        } else {
            Write-Warning "PathRAG service health check failed"
        }
    } catch {
        Write-Warning "PathRAG service is not responding"
    }
}

# Show deployment summary
function Show-Summary {
    Write-Log "`n" + "="*60
    Write-Success "PathRAG Windows Deployment Completed!"
    Write-Log "="*60
    
    Write-Host "`n🎉 Deployment Summary:" -ForegroundColor Green
    Write-Host "├─ Application Directory: $AppDir" -ForegroundColor Blue
    Write-Host "├─ Virtual Environment: $VenvPath" -ForegroundColor Blue
    Write-Host "├─ ArangoDB: http://localhost:8529" -ForegroundColor Blue
    Write-Host "├─ PathRAG API: http://localhost:$Port" -ForegroundColor Blue
    Write-Host "└─ Log File: $LogFile" -ForegroundColor Blue
    
    Write-Host "`n🔧 Service Management:" -ForegroundColor Green
    Write-Host "├─ Start service: .\deploy\deploy-windows.ps1 -Start" -ForegroundColor Blue
    Write-Host "├─ Stop service: Get-Job | Stop-Job" -ForegroundColor Blue
    Write-Host "├─ Check status: .\deploy\deploy-windows.ps1 -Status" -ForegroundColor Blue
    Write-Host "└─ Health check: .\deploy\deploy-windows.ps1 -Check" -ForegroundColor Blue
    
    Write-Host "`n📁 Important Files:" -ForegroundColor Green
    Write-Host "├─ Environment: $AppDir\.env" -ForegroundColor Blue
    Write-Host "├─ Logs: $AppDir\logs\" -ForegroundColor Blue
    Write-Host "├─ Data: $AppDir\pathrag_data\" -ForegroundColor Blue
    Write-Host "└─ Virtual Env: $VenvPath" -ForegroundColor Blue
    
    Write-Host "`n🔑 Default Credentials:" -ForegroundColor Green
    Write-Host "├─ ArangoDB: root / $ArangoPassword" -ForegroundColor Blue
    Write-Host "└─ Update credentials in: $AppDir\.env" -ForegroundColor Blue
    
    Write-Host "`n⚠️  Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Update $AppDir\.env with your API keys" -ForegroundColor Blue
    Write-Host "2. Start the service: .\deploy\deploy-windows.ps1 -Start" -ForegroundColor Blue
    Write-Host "3. Test the API: Invoke-WebRequest http://localhost:$Port/health" -ForegroundColor Blue
    Write-Host "4. Open ArangoDB web interface: http://localhost:8529" -ForegroundColor Blue
    
    Write-Log "="*60
}

# Main installation function
function Install-PathRAG {
    Write-Log "Starting PathRAG with ArangoDB installation on Windows..."
    Write-Log "Log file: $LogFile"
    
    if (-not (Test-Administrator)) {
        Write-Warning "Running without administrator privileges. Some installations may fail."
    }
    
    Test-SystemRequirements
    Install-Chocolatey
    Install-Python
    Install-Git
    Install-ArangoDB
    New-VirtualEnvironment
    Install-PythonDependencies
    Set-Environment
    Test-PathRAGSetup
    
    Show-Summary
    Write-Success "Installation completed successfully!"
}

# Show help
function Show-Help {
    Write-Host "PathRAG with ArangoDB - Windows Deployment Script" -ForegroundColor Green
    Write-Host "Usage: .\deploy-windows.ps1 [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Help              Show this help message" -ForegroundColor White
    Write-Host "  -Version           Show version information" -ForegroundColor White
    Write-Host "  -Install           Run complete installation" -ForegroundColor White
    Write-Host "  -Start             Start PathRAG service" -ForegroundColor White
    Write-Host "  -Stop              Stop PathRAG service" -ForegroundColor White
    Write-Host "  -Check             Run health checks" -ForegroundColor White
    Write-Host "  -Status            Show service status" -ForegroundColor White
    Write-Host "  -ArangoPassword    Set ArangoDB password (default: pathrag123)" -ForegroundColor White
    Write-Host "  -Port              Set API server port (default: 5000)" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\deploy-windows.ps1 -Install" -ForegroundColor Cyan
    Write-Host "  .\deploy-windows.ps1 -Start" -ForegroundColor Cyan
    Write-Host "  .\deploy-windows.ps1 -Check" -ForegroundColor Cyan
    Write-Host "  .\deploy-windows.ps1 -Install -ArangoPassword 'mypassword'" -ForegroundColor Cyan
}

# Main script logic
try {
    if ($Help) {
        Show-Help
        exit 0
    }
    
    if ($Version) {
        Write-Host "PathRAG Windows Deployment Script v1.0.0" -ForegroundColor Green
        exit 0
    }
    
    if ($Check) {
        Test-HealthChecks
        exit 0
    }
    
    if ($Status) {
        Write-Log "Checking service status..."
        
        # Check ArangoDB service
        try {
            $arangoService = Get-Service -Name "ArangoDB" -ErrorAction SilentlyContinue
            if ($arangoService) {
                Write-Info "ArangoDB Service: $($arangoService.Status)"
            } else {
                Write-Warning "ArangoDB service not found"
            }
        } catch {
            Write-Warning "Failed to check ArangoDB service status"
        }
        
        # Check running jobs
        $jobs = Get-Job | Where-Object { $_.State -eq "Running" }
        if ($jobs) {
            Write-Info "Running PathRAG jobs:"
            $jobs | ForEach-Object { Write-Info "  Job $($_.Id): $($_.Name)" }
        } else {
            Write-Info "No PathRAG jobs running"
        }
        
        exit 0
    }
    
    if ($Start) {
        Start-PathRAGService
        exit 0
    }
    
    if ($Stop) {
        Write-Log "Stopping PathRAG services..."
        Get-Job | Stop-Job
        Write-Success "PathRAG services stopped"
        exit 0
    }
    
    if ($Install) {
        Install-PathRAG
        exit 0
    }
    
    # Default action if no parameters
    Show-Help
    
} catch {
    Exit-WithError "Script execution failed: $($_.Exception.Message)"
}