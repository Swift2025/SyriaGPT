@echo off
REM Batch Script لتنفيذ أوامر التهجير داخل Docker

echo بدء تنفيذ أوامر التهجير...

REM التحقق من وجود الحاويات
echo التحقق من حالة الحاويات...
docker-compose ps

REM انتظار حتى تكون قاعدة البيانات جاهزة
echo انتظار قاعدة البيانات...
timeout /t 10 /nobreak

REM تنفيذ التهجير داخل الحاوية
echo تنفيذ التهجير...
docker-compose exec app alembic upgrade head

echo تم تنفيذ التهجير بنجاح!
pause
