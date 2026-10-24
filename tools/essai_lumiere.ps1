# Essai rapide : regenere avec ZM_SANS (prefabs exclus), synchronise et lance seulement l'eclairage
param([string]$Sans = "")
$env:ZM_SANS = $Sans
Set-Location (Split-Path $PSScriptRoot -Parent)
python tools\build_map.py | Select-Object -Last 1
.\tools\sync.ps1 -Vers Jeu | Out-Null
.\tools\compile.ps1 -Etapes Bsp, Lumiere
