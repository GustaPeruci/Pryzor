# Script de teste da API Pryzor
Write-Host "=== TESTE API PRYZOR ===" -ForegroundColor Cyan

# Teste 1: Health check
Write-Host "`n[1] Testando /health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ Health OK" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "❌ Erro: $_" -ForegroundColor Red
}

# Teste 2: Buscar jogo
Write-Host "`n[2] Testando busca de jogo (Cities: Skylines)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/games?search=Cities+Skylines&limit=1" -Method Get -TimeoutSec 10
    Write-Host "✅ Busca OK - Encontrados $($response.games.Count) jogos" -ForegroundColor Green
    $appid = $response.games[0].appid
    Write-Host "   AppID: $appid - $($response.games[0].name)" -ForegroundColor Cyan
    
    # Teste 3: Predição ML
    Write-Host "`n[3] Testando predição ML para AppID $appid..." -ForegroundColor Yellow
    $predResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/ml/predict/$appid" -Method Get -TimeoutSec 30
    Write-Host "✅ Predição OK" -ForegroundColor Green
    Write-Host "   Recomendação: $($predResponse.recommendation)" -ForegroundColor Cyan
    Write-Host "   Probabilidade: $([math]::Round($predResponse.probability * 100, 2))%" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Erro: $_" -ForegroundColor Red
}

Write-Host "`n=== FIM DOS TESTES ===" -ForegroundColor Cyan
