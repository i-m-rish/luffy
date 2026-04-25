$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RootDir

python -m pip install -r requirements-dev.txt

Write-Host "Starting Luffy local apps..."
Write-Host "IGA UI: http://127.0.0.1:8001/ui"
Write-Host "IGA API docs: http://127.0.0.1:8001/docs"
Write-Host "IdP UI: http://127.0.0.1:8002/ui"
Write-Host "IdP API docs: http://127.0.0.1:8002/docs"
Write-Host "Close this terminal or press Ctrl+C to stop."

$iga = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "fastapi_app:app", "--reload", "--port", "8001" -WorkingDirectory "$RootDir\apps\iga-service\src" -PassThru
$idp = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "fastapi_app:app", "--reload", "--port", "8002" -WorkingDirectory "$RootDir\apps\idp-service\src" -PassThru

try {
    Wait-Process -Id $iga.Id, $idp.Id
}
finally {
    Stop-Process -Id $iga.Id, $idp.Id -ErrorAction SilentlyContinue
}
