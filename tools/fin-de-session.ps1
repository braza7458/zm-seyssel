<#
Sauvegarde de fin de session : recupere la map depuis le jeu, puis envoie
tout sur GitHub s'il y a des changements.

Lance automatiquement par Claude Code a la fin de chaque reponse (hook Stop),
et utilisable a la main :
    .\tools\fin-de-session.ps1
#>
param(
    [string]$Bo3 = "D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III 455130"
)

$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

# 1. Recuperer le travail fait dans Radiant (seulement si les Mod Tools sont la)
if (Test-Path (Join-Path $Bo3 "bin\radiant_modtools.exe")) {
    & (Join-Path $PSScriptRoot "sync.ps1") -Vers Depot -Bo3 $Bo3 | Out-Null
}

# 2. Commit s'il y a quelque chose de nouveau
git add -A 2>$null
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    $date = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -q -m "Sauvegarde de fin de session ($date)"
}

# 3. Push des commits pas encore sur GitHub (y compris ceux d'un envoi rate)
$enAttente = [int](git rev-list --count "@{u}..HEAD")
if ($enAttente -eq 0) {
    exit 0
}
git push -q 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Output "{`"systemMessage`": `"Sauvegarde sur GitHub : $enAttente commit(s) envoye(s).`"}"
} else {
    Write-Output "{`"systemMessage`": `"Commit local fait, mais l'envoi sur GitHub a echoue (connexion ?). Il partira a la prochaine sauvegarde.`"}"
}
