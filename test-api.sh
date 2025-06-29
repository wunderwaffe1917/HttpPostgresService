#!/bin/bash

# Скрипт для тестирования API endpoints

API_URL="http://localhost:5000"
TOKEN=""

echo "🧪 Тестирование Flask API"
echo "========================"

# Функция для получения токена из логов
get_admin_token() {
    echo "📝 Получение админского токена из логов..."
    TOKEN=$(docker-compose logs app 2>/dev/null | grep "Created admin token:" | tail -1 | cut -d' ' -f4)
    if [ -z "$TOKEN" ]; then
        echo "❌ Не удалось получить токен из логов"
        echo "Запустите: docker-compose logs app | grep 'Created admin token'"
        exit 1
    fi
    echo "✅ Токен получен: ${TOKEN:0:20}..."
}

# Тест health check
test_health() {
    echo ""
    echo "🏥 Тест Health Check..."
    response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$API_URL/api/health")
    if [ "$response" = "200" ]; then
        echo "✅ Health check успешен"
        cat /tmp/response.json | jq . 2>/dev/null || cat /tmp/response.json
    else
        echo "❌ Health check неудачен (код: $response)"
    fi
}

# Тест создания записи
test_create_record() {
    echo ""
    echo "📝 Тест создания записи..."
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"title": "Тестовая запись", "content": "Содержимое для теста", "category": "test"}' \
        -o /tmp/response.json \
        "$API_URL/api/records")
    
    if [ "$response" = "201" ]; then
        echo "✅ Запись создана"
        cat /tmp/response.json | jq . 2>/dev/null || cat /tmp/response.json
    else
        echo "❌ Ошибка создания записи (код: $response)"
        cat /tmp/response.json
    fi
}

# Тест получения записей
test_get_records() {
    echo ""
    echo "📋 Тест получения записей..."
    response=$(curl -s -w "%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        -o /tmp/response.json \
        "$API_URL/api/records")
    
    if [ "$response" = "200" ]; then
        echo "✅ Записи получены"
        cat /tmp/response.json | jq . 2>/dev/null || cat /tmp/response.json
    else
        echo "❌ Ошибка получения записей (код: $response)"
        cat /tmp/response.json
    fi
}

# Основной процесс тестирования
main() {
    # Проверка что Docker Compose запущен
    if ! docker-compose ps | grep -q "Up"; then
        echo "❌ Docker контейнеры не запущены"
        echo "Запустите: ./docker-run.sh"
        exit 1
    fi
    
    # Получение токена
    get_admin_token
    
    # Выполнение тестов
    test_health
    test_create_record
    test_get_records
    
    echo ""
    echo "🎉 Тестирование завершено!"
    echo "🌐 Откройте $API_URL для веб-интерфейса"
}

# Запуск
main