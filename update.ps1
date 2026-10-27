<#
.SYNOPSIS
    Updates Bee With Me after new code arrived (git pull, or a copy from a USB stick), and is also
    the first run on a new machine: installs the dependencies that changed, backs the database up,
    applies new migrations, then starts the app like start.ps1.

    Needs the internet only when requirements.txt or package-lock.json changed (or on the first
    run). Everyday starts use start.ps1, which needs no internet.

    Takes the same parameters as start.ps1 (-ProjectPath, -SkipContainers, -NoBrowser).

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\update.ps1
#>

param(
    [string]$ProjectPath = $PSScriptRoot,
    [Alias('SkipDocker')]
    [switch]$SkipContainers,
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
& "$PSScriptRoot\start.ps1" -Update -ProjectPath $ProjectPath -SkipContainers:$SkipContainers -NoBrowser:$NoBrowser
