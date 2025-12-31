# set-nfs-uid-gid.ps1

# 1) Require admin
$principal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent()
)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator. Right-click PowerShell and choose 'Run as administrator'."
    exit 1
}

Write-Host "Configure Windows NFS client to use a specific Unix UID/GID."
Write-Host "You can get these values on the NAS with:  id username"
Write-Host ""

# 2) Prompt for UID and GID
$uid = Read-Host "Enter Unix UID (e.g. 1001)"
$gid = Read-Host "Enter Unix primary GID (e.g. 1007)"

if (-not ($uid -as [int]) -or -not ($gid -as [int])) {
    Write-Error "UID and GID must be numeric."
    exit 1
}

$uid = [int]$uid
$gid = [int]$gid

Write-Host ""
Write-Host "Setting AnonymousUID=$uid and AnonymousGID=$gid for Client for NFS..."

# 3) Write registry keys
$regPath = "HKLM:\SOFTWARE\Microsoft\ClientForNFS\CurrentVersion\Default"
New-Item -Path $regPath -Force | Out-Null

New-ItemProperty -Path $regPath -Name "AnonymousUID" -Value $uid -PropertyType DWord -Force | Out-Null
New-ItemProperty -Path $regPath -Name "AnonymousGID" -Value $gid -PropertyType DWord -Force | Out-Null

Write-Host ""
Write-Host "Registry updated. Any new NFS mounts after a reboot will use UID=$uid, GID=$gid."
Write-Host ""

$answer = Read-Host "Press Enter to reboot now, or type N and press Enter to cancel"

if ($answer -eq "") {
    Write-Host "Rebooting..."
    Restart-Computer -Force
} else {
    Write-Host "Reboot cancelled. Please reboot manually later to apply changes."
}
