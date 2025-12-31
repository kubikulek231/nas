# enable-nfs-client.ps1

# 1) Require admin
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator. Right-click PowerShell and choose 'Run as administrator'."
    exit 1
}

# 2) Enable NFS-related features
$features = @(
    "ServicesForNFS-ClientOnly",
    "ClientForNFS-Infrastructure",
    "NFS-Administration"
)

foreach ($f in $features) {
    Write-Host "Enabling feature: $f"
    Enable-WindowsOptionalFeature -Online -FeatureName $f -All -NoRestart -ErrorAction Stop
}

Write-Host ""
Write-Host "All requested NFS features processed."
$null = Read-Host "Press Enter to reboot now, or close this window to skip"
Write-Host "Rebooting..."
Restart-Computer -Force
