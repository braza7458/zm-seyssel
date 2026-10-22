<#
Compile la map sans passer par le Launcher, puis la lance dans le jeu.

    .\tools\compile.ps1                         tout : bsp, lumiere, link, jouer
    .\tools\compile.ps1 -Etapes Bsp,Link        seulement certaines etapes
    .\tools\compile.ps1 -Etapes Jouer           relancer la map sans recompiler

Les journaux vont dans _build\ (non publie sur GitHub).
#>
param(
    [ValidateSet("Bsp", "Lumiere", "Link", "Jouer")][string[]]$Etapes = @("Bsp", "Lumiere", "Link", "Jouer"),
    [string]$Tools = "D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III 455130",
    [string]$Jeu = "D:\SteamLibrary\steamapps\common\Call of Duty Black Ops III",
    [string]$Map = "zm_seyssel",
    [ValidateSet("low", "medium", "high")][string]$QualiteLumiere = "medium",
    # Langue du pack localise (fr_zm_seyssel.ff...) : par defaut celle du jeu installe
    [string]$Langue = ""
)

# Erreurs connues qui n'empechent pas la map de tourner : les sons perso ne compilent pas
# tant que le symbole decimal de Windows est la virgule (voir README)
$ToleresLink = "sound/zone//|sound aliases failed to load"

if (-not $Langue) {
    $langues = @{ en = "english"; fr = "french"; de = "german"; it = "italian"; es = "spanish"; pl = "polish"; ru = "russian" }
    $code = (Get-ChildItem "$Jeu\zone" -Filter "??_base.xpak" -ErrorAction SilentlyContinue | Select-Object -First 1).Name
    $Langue = if ($code -and $langues[$code.Substring(0, 2)]) { $langues[$code.Substring(0, 2)] } else { "english" }
}

$ErrorActionPreference = "Stop"
$logs = Join-Path (Split-Path $PSScriptRoot -Parent) "_build"
New-Item -ItemType Directory -Force $logs | Out-Null

# Les outils BO3 ont besoin de ces variables, que le Launcher definit normalement
$env:TA_TOOLS_PATH = "$Tools\"
$env:TA_GAME_PATH = "$Tools\"

$mapFile = "$Tools\map_source\zm\$Map.map"
$bsp = "$Tools\share\raw\maps\zm\$Map.d3dbsp"

function Etape($nom, $exe, [string[]]$arguments, [string]$toleres = "") {
    $log = Join-Path $logs "$nom.log"
    Write-Host "== $nom ..."
    $quoted = $arguments | ForEach-Object { if ($_ -match '[\s"]') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ } }
    $t = Measure-Command {
        $dir = if (Split-Path $exe) { Split-Path $exe } else { $logs }
        $p = Start-Process -FilePath $exe -ArgumentList $quoted -WorkingDirectory $dir -NoNewWindow -Wait -PassThru `
            -RedirectStandardOutput $log -RedirectStandardError "$log.err"
    }
    Get-Content "$log.err" | Add-Content $log
    Remove-Item "$log.err"
    $code = $p.ExitCode
    Write-Host ("   termine en {0:N0} s (code {1}), journal : _build\{2}.log" -f $t.TotalSeconds, $code, $nom)
    $erreurs = @(Select-String -Path $log -Pattern "^ERROR|^Error|error:|Assertion failed|LEAK" | Select-Object -First 10)
    $connues = @($erreurs | Where-Object { $toleres -and $_.Line -match $toleres })
    $graves = @($erreurs | Where-Object { -not ($toleres -and $_.Line -match $toleres) })
    if ($connues) {
        Write-Host "   avertissement connu : sons perso non compiles (symbole decimal de Windows, voir README)"
    }
    # Le linker renvoie un code non nul des qu'il y a une erreur, meme connue : on juge sur le journal
    if ($graves -or ($code -ne 0 -and -not $connues)) {
        $graves | ForEach-Object { Write-Host "   $($_.Line)" }
        throw "Echec de l'etape $nom"
    }
}

function MiseAJourGdtDB {
    # gdtdb.exe (.NET) lit les decimaux selon la langue de Windows : en francais il attend
    # "0,5" et refuse les "0.5" des fichiers BO3. On le lance donc en anglais, sans toucher a Windows.
    $dir = "$Tools\gdtdb"
    $script = @"
`$c = [Globalization.CultureInfo]::GetCultureInfo('en-US')
[Globalization.CultureInfo]::DefaultThreadCurrentCulture = `$c
[Threading.Thread]::CurrentThread.CurrentCulture = `$c
Set-Location '$dir'
[Environment]::CurrentDirectory = '$dir'
`$a = [Reflection.Assembly]::LoadFrom('$dir\gdtdb.exe')
exit [int]`$a.EntryPoint.Invoke(`$null, @(,[string[]]@('/update')))
"@
    $encode = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
    Etape "gdtdb" "powershell" @("-NoProfile", "-EncodedCommand", $encode)
}

if ($Etapes -contains "Bsp") {
    MiseAJourGdtDB
    New-Item -ItemType Directory -Force (Split-Path $bsp) | Out-Null
    Etape "bsp" "$Tools\bin\cod2map64.exe" @("-platform", "pc", "-navmesh", "-navvolume", "-loadFrom", $mapFile, $bsp)
}
if ($Etapes -contains "Lumiere") {
    # Pas de "-platform pc" ici : Radiant est une appli Qt qui le prend pour son propre plugin
    Etape "lumiere" "$Tools\bin\radiant_modtools.exe" @("-ledSilent", "+$QualiteLumiere", "+localprobes", "+forceclean", $mapFile)
}
if ($Etapes -contains "Link") {
    # Le jeu charge <langue>_<map>.ff : un jeu en francais exige fr_zm_seyssel.ff
    Etape "link" "$Tools\bin\linker_modtools.exe" @("-language", $Langue, "-modsource", $Map) $ToleresLink
}
if ($Etapes -contains "Jouer") {
    # Le jeu lit usermaps\ dans son propre dossier : un lien pointe vers celui des Mod Tools
    if (-not (Test-Path "$Jeu\usermaps")) {
        New-Item -ItemType Junction -Path "$Jeu\usermaps" -Target "$Tools\usermaps" | Out-Null
    }
    if (-not (Test-Path "$Tools\usermaps\$Map\zone\$($Langue.Substring(0, 2))_$Map.ff")) {
        throw "Pas de pack $($Langue.Substring(0, 2))_$Map.ff : lance d'abord l'etape Link"
    }
    Write-Host "== lancement de $Map"
    Start-Process -FilePath "$Jeu\BlackOps3.exe" -WorkingDirectory $Jeu -ArgumentList "+devmap", $Map
}
