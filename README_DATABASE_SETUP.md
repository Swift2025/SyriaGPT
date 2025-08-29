# إعداد قاعدة البيانات - SyriaGPT

## نظرة عامة

هذا الدليل يوضح كيفية إعداد قاعدة البيانات وتشغيل أوامر التهجير (migrations) باستخدام Docker.

## الملفات المتاحة

### ملفات التشغيل

1. **`setup_database.bat`** - ملف شامل لإعداد قاعدة البيانات
2. **`create_migration.bat`** - إنشاء migration جديد
3. **`run_migrations.bat`** - تطبيق التهجير الموجود
4. **`run_migrations.ps1`** - PowerShell script للتهجير
5. **`run_migrations.sh`** - Bash script للتهجير (Linux/Mac)

## كيفية الاستخدام

### الطريقة الأولى: استخدام الملف الشامل (مُوصى به)

```bash
# تشغيل الملف الشامل
setup_database.bat
```

هذا الملف سيقوم بـ:
- التحقق من وجود Docker
- تشغيل الحاويات
- إنشاء migration جديد للجدولين
- تطبيق التهجير
- عرض حالة التهجير

### الطريقة الثانية: خطوات منفصلة

#### 1. تشغيل الحاويات
```bash
docker-compose up -d
```

#### 2. إنشاء migration جديد
```bash
# باستخدام batch file
create_migration.bat

# أو مباشرة
docker-compose exec app alembic revision --autogenerate -m "add_questions_and_answers_tables"
```

#### 3. تطبيق التهجير
```bash
# باستخدام batch file
run_migrations.bat

# أو مباشرة
docker-compose exec app alembic upgrade head
```

#### 4. التحقق من حالة التهجير
```bash
docker-compose exec app alembic current
```

## أوامر مفيدة

### عرض حالة التهجير
```bash
docker-compose exec app alembic current
```

### عرض تاريخ التهجير
```bash
docker-compose exec app alembic history
```

### التراجع عن آخر تهجير
```bash
docker-compose exec app alembic downgrade -1
```

### التراجع عن جميع التهجيرات
```bash
docker-compose exec app alembic downgrade base
```

### إعادة تطبيق جميع التهجيرات
```bash
docker-compose exec app alembic upgrade head
```

## الوصول إلى الخدمات

بعد تشغيل الحاويات، يمكنك الوصول إلى:

- **التطبيق الرئيسي**: http://localhost:9000
- **واجهة قاعدة البيانات (pgAdmin)**: http://localhost:5050
  - البريد الإلكتروني: admin@admin.com
  - كلمة المرور: admin123

## استكشاف الأخطاء

### مشكلة: لا يمكن الاتصال بقاعدة البيانات
```bash
# التحقق من حالة الحاويات
docker-compose ps

# عرض سجلات قاعدة البيانات
docker-compose logs db
```

### مشكلة: فشل في التهجير
```bash
# التحقق من سجلات التطبيق
docker-compose logs app

# إعادة تشغيل الحاويات
docker-compose restart
```

### مشكلة: Docker غير متاح
```bash
# التحقق من تثبيت Docker
docker --version

# تشغيل Docker Desktop (Windows/Mac)
# أو تشغيل خدمة Docker (Linux)
```

## ملاحظات مهمة

1. **انتظار قاعدة البيانات**: تأكد من انتظار 10-15 ثانية بعد تشغيل الحاويات قبل تنفيذ أوامر التهجير.

2. **البيانات المحفوظة**: البيانات محفوظة في volume Docker، لذا لن تفقدها عند إعادة تشغيل الحاويات.

3. **النسخ الاحتياطية**: يمكنك إنشاء نسخة احتياطية من قاعدة البيانات باستخدام pgAdmin.

4. **إعادة تعيين قاعدة البيانات**: لحذف جميع البيانات وإعادة البدء:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

## الجداول المتوقعة

بعد تنفيذ التهجير، ستجد الجداول التالية:

1. **`users`** - جدول المستخدمين
2. **`questions`** - جدول الأسئلة
3. **`answers`** - جدول الإجابات

## الدعم

إذا واجهت أي مشاكل، تأكد من:
- تشغيل Docker Desktop
- وجود مساحة كافية على القرص
- عدم استخدام المنافذ 9000 أو 5050 أو 5432 من قبل تطبيقات أخرى
