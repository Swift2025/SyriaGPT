@echo off
REM Batch Script لإنشاء migration جديد

echo إنشاء migration جديد...

REM التحقق من وجود الحاويات
echo التحقق من حالة الحاويات...
docker-compose ps

REM إنشاء migration جديد
echo إنشاء migration جديد...
docker-compose exec app alembic revision --autogenerate -m "add_questions_and_answers_tables"

echo تم إنشاء migration بنجاح!
pause
