Get-NetTCPConnection -LocalPort 8003 | ForEach-Object {
    $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
    Write-Host "PID: $($_.OwningProcess) - Name: $($proc.ProcessName) - Path: $($proc.Path)"
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2
Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue | Format-Table LocalPort, State, OwningProcess