# compactar-wsl.ps1
# Libera espacio de WSL y se lo devuelve a Windows:
#   1. Borra los node_modules dentro de ~/GitHub (repos y worktrees de agentes) que
#      NO esten en uso. Los que esten en uso se saltean. Se regeneran con npm install.
#   2. Compacta los VHDX (lo que haria el modo sparse). Esto SI apaga WSL.
# Los VHDX de WSL crecen solos y nunca se achican: si borras 20 GB dentro de
# Ubuntu, el archivo sigue ocupando lo mismo en C: hasta que se compacta.
#
# Modos:
#   (sin parametros)  manual, pregunta antes de borrar y de compactar. Lo abre
#                     "Compactar WSL.cmd" del Escritorio.
#   -Auto             lo corre la tarea programada cada 15 min. No pregunta nada:
#                     sale sin tocar nada salvo que C: tenga menos de -MinLibreGB
#                     libres Y esten cerrados WSL, VS Code, Cursor y Docker Desktop.
#   -Instalar         registra la tarea programada (una sola vez, como admin).
#   -Desinstalar      la borra.
#
# Por que existe -Auto: el 2026-10-17 C: llego a 0 bytes libres. WhatsApp y
# Discord perdieron la sesion y hubo que reenlazarlos desde el celular. Esperar a
# que el operador se acuerde de compactar es esperar a que el disco se llene.
#
# Fuente versionada en my-awi-instance: .claude/skills/shared/scripts/windows/.
# Lo que corre es la copia en %USERPROFILE%\scripts\.
# Solo ASCII a proposito: PowerShell 5.1 lee mal los acentos en .ps1 sin BOM.

param(
    [switch]$Auto,
    [switch]$Instalar,
    [switch]$Desinstalar,
    [double]$MinLibreGB = 15
)

$tarea = 'Compactar WSL automatico'
$estadoDir = Join-Path $env:LOCALAPPDATA 'compactar-wsl'
$estadoFile = Join-Path $estadoDir 'estado.json'
# Si una compactacion no alcanzo a dejar C: sobre el minimo, repetirla cada 15
# min no recupera nada mas: solo apaga WSL de nuevo.
$pausaEntreIntentosH = 6
# El aviso de "cerra todo para compactar" no se repite mas seguido que esto.
$pausaEntreAvisosH = 2
$appsQueUsanWSL = @(
    @{ Proc = 'Docker Desktop'; Nombre = 'Docker Desktop (icono de la bandeja > Quit Docker Desktop)' },
    @{ Proc = 'Code'; Nombre = 'VS Code' },
    @{ Proc = 'Cursor'; Nombre = 'Cursor' })

function LibreC { [math]::Round((Get-Volume C).SizeRemaining / 1GB, 2) }
function TamGB($p) { [math]::Round((Get-Item $p).Length / 1GB, 2) }
function Salir($code) {
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    if (-not $Auto) { Read-Host 'Enter para cerrar' }
    exit $code
}
# Ruta de Windows -> ruta vista desde WSL (C:\x\y -> /mnt/c/x/y)
function RutaWSL($p) { '/mnt/' + $p.Substring(0, 1).ToLower() + ($p.Substring(2) -replace '\\', '/') }

function Avisar($titulo, $texto) {
    try {
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $t = [Security.SecurityElement]::Escape($titulo)
        $c = [Security.SecurityElement]::Escape($texto)
        $xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>$t</text><text>$c</text></binding></visual></toast>")
        $app = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app).Show([Windows.UI.Notifications.ToastNotification]::new($xml))
    } catch { Write-Host "No pude mostrar el aviso: $($_.Exception.Message)" }
}

function LeerEstado {
    try { return Get-Content $estadoFile -Raw | ConvertFrom-Json } catch { return [pscustomobject]@{} }
}
function GuardarEstado($clave) {
    $e = LeerEstado
    $e | Add-Member -NotePropertyName $clave -NotePropertyValue (Get-Date).ToString('o') -Force
    New-Item -ItemType Directory -Force -Path $estadoDir | Out-Null
    $e | ConvertTo-Json | Set-Content -Path $estadoFile -Encoding ASCII
}
function HorasDesde($clave) {
    $v = (LeerEstado).$clave
    if (-not $v) { return [double]::MaxValue }
    return ((Get-Date) - [datetime]$v).TotalHours
}

function WSLCorriendo { [bool](Get-Process vmmem, vmmemWSL -ErrorAction SilentlyContinue) }
function AppsAbiertas { @($appsQueUsanWSL | Where-Object { Get-Process $_.Proc -ErrorAction SilentlyContinue }) }

# ---------------------------------------------------------------------------
# Instalacion de la tarea programada
# ---------------------------------------------------------------------------
if ($Instalar -or $Desinstalar) {
    Unregister-ScheduledTask -TaskName $tarea -Confirm:$false -ErrorAction SilentlyContinue
    if ($Desinstalar) { Write-Host "Tarea '$tarea' borrada."; Read-Host 'Enter para cerrar'; exit 0 }
    # conhost --headless: sin esto aparece una ventana de PowerShell cada 15 min.
    $argumentos = '--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $PSCommandPath + '" -Auto'
    $accion = New-ScheduledTaskAction -Execute 'conhost.exe' -Argument $argumentos
    $cada15 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15)
    $alEntrar = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
    # RunLevel Highest es lo que evita el "si" de cada vez: la tarea ya nace elevada.
    # Interactive: corre en tu sesion, asi puede mostrar los avisos de Windows.
    $quien = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
    $ajustes = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
        -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $tarea -Action $accion -Trigger $cada15, $alEntrar -Principal $quien -Settings $ajustes `
        -Description "Compacta WSL y Docker cuando C: baja de $MinLibreGB GB y estan cerrados. Fuente: $PSCommandPath" | Out-Null
    Write-Host "Tarea '$tarea' instalada: revisa cada 15 min, compacta si C: < $MinLibreGB GB y WSL esta cerrado." -ForegroundColor Green
    Write-Host "Log: $env:TEMP\compactar-wsl.log"
    Read-Host 'Enter para cerrar'
    exit 0
}

$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) {
    Write-Host 'Hace falta ejecutarlo como administrador. Usa "Compactar WSL.cmd".' -ForegroundColor Red
    Salir 1
}

# ---------------------------------------------------------------------------
# -Auto: decidir si hay que hacer algo, antes de escribir ningun log.
# Casi todas las corridas salen aca, en silencio.
# ---------------------------------------------------------------------------
if ($Auto) {
    $libre = LibreC
    if ($libre -ge $MinLibreGB) { exit 0 }
    $abiertas = AppsAbiertas
    if ((WSLCorriendo) -or $abiertas.Count -gt 0) {
        if ((HorasDesde 'ultimoAviso') -ge $pausaEntreAvisosH) {
            Avisar "C: tiene $libre GB libres" 'Cuando termines, cerra VS Code, Cursor y Docker: WSL se compacta solo apenas este cerrado.'
            GuardarEstado 'ultimoAviso'
        }
        exit 0
    }
    if ((HorasDesde 'ultimoIntento') -lt $pausaEntreIntentosH) { exit 0 }
    GuardarEstado 'ultimoIntento'
}

$log = Join-Path $env:TEMP 'compactar-wsl.log'
Start-Transcript -Path $log -Force | Out-Null
if ($Auto) {
    Write-Host "Modo automatico: C: tiene $(LibreC) GB libres (minimo $MinLibreGB) y WSL esta cerrado."
    Avisar 'Compactando WSL' 'Tarda unos minutos. Hasta que avise que termino, no abras VS Code ni Docker.'
}

# ---------------------------------------------------------------------------
# Script que corre DENTRO de Linux (como root, para poder leer /proc de todos).
#   medir  -> lista cada node_modules de ~/GitHub como LIBRE o EN USO, con su tamano
#   borrar -> borra los LIBRES; antes de cada uno vuelve a mirar /proc por si
#             algo lo empezo a usar mientras tanto
#   runner -> imprime algo si un runner de GitHub Actions esta corriendo un job
# "En uso" = algun proceso:
#   - tiene su directorio de trabajo dentro del proyecto (agente, npm, dev server, tests), o
#   - tiene abierto un archivo dentro de ese node_modules, o
#   - tiene mapeado en memoria un archivo de ahi (modulos nativos .node, binarios).
# Los node_modules de ~/.nvm (paquetes globales, incluido claude) y de
# ~/.vscode-server (extensiones) NO se tocan: no se regeneran solos.
# ---------------------------------------------------------------------------
$bash = @'
#!/bin/bash
if [ "$1" = "runner" ]; then pgrep -af Runner.Worker; exit 0; fi

SNAP=$(mktemp)
trap 'rm -f "$SNAP"' EXIT

# Foto de lo que usa cada proceso: "tipo /proc/PID/... ruta"
foto() {
  {
    find /proc/[0-9]*/cwd -maxdepth 0 -printf 'cwd %h %l\n' 2>/dev/null
    find /proc/[0-9]*/fd -mindepth 1 -maxdepth 1 -printf 'fd %h %l\n' 2>/dev/null
    awk '$6 ~ /^\/home\// { print "map", FILENAME, $6 }' /proc/[0-9]*/maps 2>/dev/null
  } > "$SNAP"
}

# Imprime "PID comando (motivo)" del primer proceso que usa $1 (un node_modules), o nada
quien_usa() {
  local hit pid
  hit=$(awk -v nm="$1/" -v pj="${1%/node_modules}" '
    # cwd dentro del proyecto. Un agente en una worktree NO bloquea al repo padre.
    $1 == "cwd" && ($3 == pj || index($3, pj "/") == 1) && index($3, pj "/.claude/worktrees/") != 1 { print $2, "trabaja en la carpeta"; exit }
    $1 == "fd"  && index($3, nm) == 1 { print $2, "tiene un archivo abierto"; exit }
    $1 == "map" && index($3, nm) == 1 { print $2, "tiene un modulo cargado"; exit }
  ' "$SNAP")
  [ -z "$hit" ] && return 1
  pid=$(echo "${hit%% *}" | cut -d/ -f3)   # "/proc/123" o "/proc/123/fd" -> 123
  echo "$pid $(cat /proc/$pid/comm 2>/dev/null) (${hit#* })"
}

corto() { echo "$1" | sed -E 's#^/home/[^/]+/GitHub/##; s#/_data/organizations/#/../#; s#/node_modules$##'; }

mapfile -t L < <(find /home/*/GitHub -xdev -type d -name node_modules -prune 2>/dev/null | sort)
foto

if [ "$1" = "medir" ]; then
  nl=0; ml=0; nu=0; mu=0
  for d in "${L[@]}"; do
    mb=$(du -sm "$d" 2>/dev/null | cut -f1)
    if u=$(quien_usa "$d"); then
      nu=$((nu+1)); mu=$((mu+mb)); printf '  EN USO %6s MB  %s  <- %s\n' "$mb" "$(corto "$d")" "$u"
    else
      nl=$((nl+1)); ml=$((ml+mb)); printf '  libre  %6s MB  %s\n' "$mb" "$(corto "$d")"
    fi
  done
  echo "RESUMEN $nl $ml $nu $mu"

elif [ "$1" = "borrar" ]; then
  n=0; s=0; e=0
  for d in "${L[@]}"; do
    foto   # foto nueva justo antes de cada borrado
    if u=$(quien_usa "$d"); then
      s=$((s+1)); echo "  salteado (en uso): $(corto "$d") <- $u"; continue
    fi
    if rm -rf -- "$d"; then n=$((n+1)); else e=$((e+1)); echo "  error al borrar: $(corto "$d")"; fi
  done
  echo "  borrados: $n   salteados por estar en uso: $s   con error: $e"
  echo "  fstrim (avisa al disco virtual que esos bloques quedaron libres):"
  fstrim -av
fi
'@

# 1. Buscar los VHDX: cada distro registrada + el disco de datos de Docker
$discos = @()
Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' -ErrorAction SilentlyContinue | ForEach-Object {
    $p = Get-ItemProperty $_.PSPath
    if (-not $p.BasePath) { return }
    $base = $p.BasePath -replace '^\\\\\?\\', ''
    $nombre = if ($p.VhdFileName) { $p.VhdFileName } else { 'ext4.vhdx' }
    $f = Join-Path $base $nombre
    if (Test-Path $f) { $discos += [pscustomobject]@{ Distro = $p.DistributionName; Ruta = $f } }
}
$dockerData = Join-Path $env:LOCALAPPDATA 'Docker\wsl\disk\docker_data.vhdx'
if (Test-Path $dockerData) { $discos += [pscustomobject]@{ Distro = 'docker-data'; Ruta = $dockerData } }
if ($discos.Count -eq 0) { Write-Host 'No encontre ningun VHDX de WSL.'; Salir 1 }
$distrosLinux = @($discos | Where-Object { $_.Distro -notin @('docker-data', 'docker-desktop') })

Write-Host ''
Write-Host "C: libre antes: $(LibreC) GB" -ForegroundColor Cyan
$antes = @{}
foreach ($d in $discos) { $antes[$d.Ruta] = TamGB $d.Ruta; Write-Host ("  {0,-15} {1,8} GB  {2}" -f $d.Distro, $antes[$d.Ruta], $d.Ruta) }

# 2. node_modules: medir, confirmar, borrar los libres. WSL puede seguir funcionando.
#    En -Auto se borran todos los libres sin medir ni preguntar.
$sh = Join-Path $env:TEMP 'compactar-wsl-nm.sh'
[IO.File]::WriteAllText($sh, ($bash -replace "`r", ''), [Text.Encoding]::ASCII)
$shWSL = RutaWSL $sh

foreach ($d in $distrosLinux) {
    Write-Host ''
    if ($Auto) {
        Write-Host "node_modules en ~/GitHub de $($d.Distro): borrando los que no estan en uso..." -ForegroundColor Cyan
        wsl -d $d.Distro -u root -- bash $shWSL borrar | Out-Host
        continue
    }
    Write-Host "node_modules en ~/GitHub de $($d.Distro) (midiendo, puede tardar un par de minutos)..." -ForegroundColor Cyan
    $salida = wsl -d $d.Distro -u root -- bash $shWSL medir
    if ($LASTEXITCODE -ne 0 -or -not $salida) {
        Write-Host "  $($d.Distro) no arranco o fallo la busqueda. Salteo esta distro." -ForegroundColor Yellow
        continue
    }
    $salida | Where-Object { $_ -notmatch '^RESUMEN' } | ForEach-Object {
        if ($_ -match 'EN USO') { Write-Host $_ -ForegroundColor Yellow } else { Write-Host $_ }
    }
    $r = ($salida | Where-Object { $_ -match '^RESUMEN' } | Select-Object -Last 1) -split '\s+'
    $nl = [int]$r[1]; $ml = [double]$r[2]; $nu = [int]$r[3]; $mu = [double]$r[4]
    Write-Host ''
    Write-Host ("  Libres: {0} ({1:N1} GB)   En uso, no se tocan: {2} ({3:N1} GB)" -f $nl, ($ml / 1024), $nu, ($mu / 1024))
    if ($nl -eq 0) { continue }
    $ok = Read-Host '  Borrar los libres? (s/n)'
    if ($ok -match '^[sS]') {
        wsl -d $d.Distro -u root -- bash $shWSL borrar | Out-Host
    } else {
        Write-Host '  No se borro nada.'
    }
}

# 3. Compactar: necesita apagar WSL
Write-Host ''
Write-Host "C: libre ahora: $(LibreC) GB" -ForegroundColor Cyan
if ($Auto) {
    # Arrancar WSL para borrar levanta los runners de Actions: si alguno ya tomo
    # un job, apagar WSL se lo corta. Se deja para la proxima vuelta.
    foreach ($d in $distrosLinux) {
        $jobs = wsl -d $d.Distro -u root -- bash $shWSL runner
        if ($jobs) {
            Write-Host "Un runner de Actions esta corriendo un job en $($d.Distro). No compacto esta vez." -ForegroundColor Yellow
            Remove-Item $sh -Force -ErrorAction SilentlyContinue
            Avisar 'Compactacion postergada' 'Un runner de GitHub Actions esta corriendo un job. Se reintenta mas tarde.'
            Salir 0
        }
    }
    # Pudiste abrir VS Code o Docker mientras borraba: entonces no se apaga nada.
    $abiertas = AppsAbiertas
    if ($abiertas.Count -gt 0) {
        Write-Host "Se abrio $($abiertas[0].Nombre) mientras borraba. No compacto." -ForegroundColor Yellow
        Remove-Item $sh -Force -ErrorAction SilentlyContinue
        Avisar 'Compactacion cancelada' "Se abrio $($abiertas[0].Nombre). Los node_modules ya se borraron; la compactacion queda para mas tarde."
        Salir 0
    }
} else {
    Write-Host 'Lo borrado ya quedo libre DENTRO de Ubuntu, pero el VHDX en C: no se achica hasta compactar.'
    Write-Host 'Compactar APAGA WSL: corta VS Code remoto, Docker, agentes y runners.' -ForegroundColor Yellow
    $ok = Read-Host 'Compactar ahora? (s/n)'
    if ($ok -notmatch '^[sS]') { Write-Host 'Listo, sin compactar. Podes volver a correr el script mas tarde.'; Remove-Item $sh -Force -ErrorAction SilentlyContinue; Salir 0 }

    foreach ($app in $appsQueUsanWSL) {
        while (Get-Process $app.Proc -ErrorAction SilentlyContinue) {
            Write-Host "$($app.Nombre) esta abierto. Cerralo (si no, vuelve a levantar WSL a mitad de la compactacion)." -ForegroundColor Yellow
            Read-Host 'Cuando lo hayas cerrado, presiona Enter'
        }
    }
}
Remove-Item $sh -Force -ErrorAction SilentlyContinue

Write-Host 'Apagando WSL...' -ForegroundColor Cyan
wsl --shutdown
$t = 0
while ((WSLCorriendo) -and $t -lt 60) { Start-Sleep 2; $t += 2 }
if (WSLCorriendo) {
    Write-Host 'La VM de WSL sigue viva despues de 60 s. Cerra terminales de Ubuntu y volve a correr el script.' -ForegroundColor Red
    if ($Auto) { Avisar 'Compactacion cancelada' 'WSL no se apago en 60 segundos. Se reintenta mas tarde.' }
    Salir 1
}
Start-Sleep 3

foreach ($d in $discos) {
    Write-Host ''
    Write-Host "Compactando $($d.Distro) ($($antes[$d.Ruta]) GB)... puede tardar varios minutos" -ForegroundColor Cyan
    $dp = Join-Path $env:TEMP 'compactar-wsl-diskpart.txt'
    @(
        "select vdisk file=`"$($d.Ruta)`""
        'attach vdisk readonly'
        'compact vdisk'
        'detach vdisk'
        'exit'
    ) | Set-Content -Path $dp -Encoding ASCII
    diskpart /s $dp | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  diskpart devolvio $LASTEXITCODE en $($d.Distro). Intento soltar el disco por las dudas." -ForegroundColor Yellow
        @("select vdisk file=`"$($d.Ruta)`"", 'detach vdisk', 'exit') | Set-Content -Path $dp -Encoding ASCII
        diskpart /s $dp | Out-Null
    }
    Remove-Item $dp -Force -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host '================ RESULTADO ================' -ForegroundColor Green
$total = 0
foreach ($d in $discos) {
    $despues = TamGB $d.Ruta
    $dif = [math]::Round($antes[$d.Ruta] - $despues, 2)
    $total += $dif
    Write-Host ("  {0,-15} {1,8} GB -> {2,8} GB   (recuperado {3} GB)" -f $d.Distro, $antes[$d.Ruta], $despues, $dif)
}
Write-Host "  Total recuperado: $([math]::Round($total, 2)) GB"
Write-Host "  C: libre ahora:   $(LibreC) GB" -ForegroundColor Green
Write-Host "  Log: $log"
if ($Auto) { Avisar 'WSL compactado' "Recuperados $([math]::Round($total, 1)) GB. C: tiene $(LibreC) GB libres. Ya podes abrir VS Code y Docker." }
Salir 0
