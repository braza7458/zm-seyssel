<#
Synchronise les sources de la map entre ce depot et le dossier de BO3.

    .\tools\sync.ps1 -Vers Jeu      copie le depot vers le jeu (apres un git pull)
    .\tools\sync.ps1 -Vers Depot    copie le jeu vers le depot (avant un git commit)

Rien n'est jamais supprime : robocopy /E ajoute et met a jour seulement.
Les fichiers compiles (usermaps\<map>\zone) ne sont pas copies.
#>
param(
    [Parameter(Mandatory)][ValidateSet("Jeu", "Depot")][string]$Vers,
    [string]$Bo3 = "D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III",
    [string]$Map = "zm_seyssel"
)

$repo = Join-Path (Split-Path $PSScriptRoot -Parent) "game"

if (-not (Test-Path (Join-Path $Bo3 "bin\radiant_modtools.exe"))) {
    Write-Error "Mod Tools introuvables dans $Bo3. Installe 'Call of Duty: Black Ops III - Mod Tools' depuis Steam (Bibliotheque > Outils)."
    exit 1
}

# Dossiers synchronises (chemin relatif identique dans le jeu et dans game\)
$dirs = @("map_source\_prefabs\$Map", "usermaps\$Map")
$files = @("map_source\zm\$Map.map")

foreach ($d in $dirs) {
    $src, $dst = if ($Vers -eq "Jeu") { (Join-Path $repo $d), (Join-Path $Bo3 $d) } else { (Join-Path $Bo3 $d), (Join-Path $repo $d) }
    if (Test-Path $src) {
        robocopy $src $dst /E /XD zone /XF *.ff *.xpak *.bak /NJH /NJS /NDL /NP | Out-Host
    }
}

foreach ($f in $files) {
    $src, $dst = if ($Vers -eq "Jeu") { (Join-Path $repo $f), (Join-Path $Bo3 $f) } else { (Join-Path $Bo3 $f), (Join-Path $repo $f) }
    if (Test-Path $src) {
        New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
        Copy-Item $src $dst -Force
        Write-Host "copie : $f"
    }
}

Write-Host "Synchro terminee ($Vers)."
