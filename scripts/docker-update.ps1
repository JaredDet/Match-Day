param(
    [switch]$SeedDemo
)

$ErrorActionPreference = "Stop"

$composeFile = Join-Path $PSScriptRoot "..\docker-compose.yml"
$applicationServices = @(
    "backend",
    "match-clock-worker",
    "news-worker",
    "recommendations-worker",
    "frontend"
)

Write-Host "Construyendo las imágenes de Matchday..."
docker compose -f $composeFile build
if ($LASTEXITCODE -ne 0) { throw "No se pudieron construir las imágenes." }

Write-Host "Comprobando PostgreSQL y Redis..."
docker compose -f $composeFile up -d --wait postgres redis
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL o Redis no quedaron disponibles." }

Write-Host "Aplicando migraciones..."
docker compose -f $composeFile run --rm initialize
if ($LASTEXITCODE -ne 0) { throw "Falló la inicialización de la base de datos." }

if ($SeedDemo) {
    Write-Host "Cargando datos demo..."
    docker compose -f $composeFile --profile demo run --rm seed-demo
    if ($LASTEXITCODE -ne 0) { throw "Falló la carga de datos demo." }
}

Write-Host "Publicando API, workers y frontend con las imágenes nuevas..."
docker compose -f $composeFile up -d --force-recreate --wait @applicationServices
if ($LASTEXITCODE -ne 0) { throw "Uno o más servicios no quedaron saludables." }

docker compose -f $composeFile ps
Write-Host "Matchday actualizado en http://localhost:3000"
