# PowerShell Script لتنفيذ أوامر التهجير داخل Docker

Write-Host "بدء تنفيذ أوامر التهجير..." -ForegroundColor Green

# التحقق من وجود الحاويات
Write-Host "التحقق من حالة الحاويات..." -ForegroundColor Yellow
docker-compose ps

# انتظار حتى تكون قاعدة البيانات جاهزة
Write-Host "انتظار قاعدة البيانات..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# تنفيذ التهجير داخل الحاوية
Write-Host "تنفيذ التهجير..." -ForegroundColor Yellow
docker-compose exec app alembic upgrade head

Write-Host "تم تنفيذ التهجير بنجاح!" -ForegroundColor Green
