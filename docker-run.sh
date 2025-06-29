#!/bin/bash

# Скрипт для быстрого запуска приложения в Docker

echo "🐳 Запуск Flask API в Docker контейнере..."

# Остановка и удаление существующих контейнеров
echo "Остановка существующих контейнеров..."
docker-compose down

# Сборка и запуск
echo "Сборка и запуск контейнеров..."
docker-compose up --build -d

echo "✅ Контейнеры запущены!"
echo ""
echo "🌐 API доступен по адресу: http://localhost:5000"
echo "🗄️  База данных: localhost:5432"
echo ""
echo "📋 Для просмотра логов используйте:"
echo "   docker-compose logs -f app"
echo ""
echo "🛑 Для остановки используйте:"
echo "   docker-compose down"