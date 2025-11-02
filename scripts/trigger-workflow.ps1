# PowerShell script to trigger workflow
Write-Host "🚀 Triggering Crypto Volatility Alerts workflow..." -ForegroundColor Cyan

gh workflow run volatality.yml

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Workflow triggered successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏳ Waiting for workflow to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    Write-Host ""
    Write-Host "📊 Latest workflow runs:" -ForegroundColor Cyan
    gh run list --workflow=volatality.yml --limit 3
    
    Write-Host ""
    Write-Host "💡 To watch the run live, use:" -ForegroundColor Yellow
    Write-Host "   gh run watch" -ForegroundColor White
} else {
    Write-Host "❌ Failed to trigger workflow" -ForegroundColor Red
    Write-Host "Make sure you're authenticated: gh auth login" -ForegroundColor Yellow
}

