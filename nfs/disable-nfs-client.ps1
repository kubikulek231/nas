# disable-nfs-client.ps1

# 1) Require admin
$principal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent()
)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator. Right-click PowerShell and choose 'Run as administrator'."
    exit 1
}

# 2) Disable NFS-related features
$features = @(
    "ServicesForNFS-ClientOnly",
    "ClientForNFS-Infrastructure",
    "NFS-Administration"
)

foreach ($f in $features) {
    Write-Host "Disabling feature: $f"
    Disable-WindowsOptionalFeature -Online -FeatureName $f -NoRestart -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "All requested NFS features processed."
$null = Read-Host "Press Enter to reboot now, or close this window to skip"
Write-Host "Rebooting..."
Restart-Computer -Force
