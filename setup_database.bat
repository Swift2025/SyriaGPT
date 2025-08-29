@echo off
REM Batch Script شامل لإعداد قاعدة البيانات

echo ========================================
echo إعداد قاعدة البيانات - SyriaGPT
echo ========================================

REM التحقق من وجود Docker
echo التحقق من وجود Docker...
docker --version
if %errorlevel% neq 0 (
    echo خطأ: Docker غير مثبت أو غير متاح
    pause
    exit /b 1
)

REM تشغيل الحاويات
echo تشغيل الحاويات...
docker-compose up -d

REM انتظار قاعدة البيانات
echo انتظار قاعدة البيانات...
timeout /t 15 /nobreak

REM إنشاء migration جديد
echo إنشاء migration جديد...
docker-compose exec app alembic revision --autogenerate -m "add_questions_and_answers_tables"

REM تطبيق التهجير
echo تطبيق التهجير...
docker-compose exec app alembic upgrade head

REM التحقق من حالة التهجير
echo التحقق من حالة التهجير...
docker-compose exec app alembic current

echo ========================================
echo تم إعداد قاعدة البيانات بنجاح!
echo ========================================
echo يمكنك الآن الوصول إلى:
echo - التطبيق: http://localhost:9000
echo - قاعدة البيانات: http://localhost:5050
echo ========================================
pause
