#!/bin/bash

# Script لتنفيذ أوامر التهجير داخل Docker

echo "بدء تنفيذ أوامر التهجير..."

# التحقق من وجود الحاويات
echo "التحقق من حالة الحاويات..."
docker-compose ps

# انتظار حتى تكون قاعدة البيانات جاهزة
echo "انتظار قاعدة البيانات..."
sleep 10

# تنفيذ التهجير داخل الحاوية
echo "تنفيذ التهجير..."
docker-compose exec app alembic upgrade head

echo "تم تنفيذ التهجير بنجاح!"
