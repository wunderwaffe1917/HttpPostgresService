# Примеры использования динамического API

## Базовые операции

### 1. Получение списка схем
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5000/api/db/schemas
```

### 2. Получение таблиц в схеме
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5000/api/db/schemas/public/tables
```

### 3. Получение колонок таблицы
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5000/api/db/schemas/public/tables/data_records/columns
```

## Поиск по колонкам

### Поиск по id_template = "123"
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"schema": "public", "table": "data_records", "filters": {"id_template": "123"}}' \
     http://localhost:5000/api/db/search
```

### Поиск по нескольким условиям
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "schema": "public", 
       "table": "data_records", 
       "filters": {
         "category": "test", 
         "is_active": true
       },
       "limit": 50
     }' \
     http://localhost:5000/api/db/search
```

### Поиск через URL параметры
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:5000/api/db/schemas/public/tables/data_records/data?id_template=123&limit=10"
```

## Операции с данными

### Вставка новой записи
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "data": {
         "title": "Новая запись", 
         "content": "Содержимое", 
         "category": "example",
         "id_template": "999"
       }
     }' \
     http://localhost:5000/api/db/schemas/public/tables/data_records/data
```

### Обновление записи
```bash
curl -X PUT \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "data": {"title": "Обновленный заголовок"},
       "filters": {"id_template": "123"}
     }' \
     http://localhost:5000/api/db/schemas/public/tables/data_records/data
```

### Удаление записи
```bash
curl -X DELETE \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "filters": {"id_template": "999"}
     }' \
     http://localhost:5000/api/db/schemas/public/tables/data_records/data
```

## Практические примеры

### Найти все записи с определенным шаблоном
```javascript
// Через веб-интерфейс /dynamic
// 1. Выберите схему: public
// 2. Выберите таблицу: data_records  
// 3. В поле "Название колонки": id_template
// 4. В поле "Значение для поиска": 123
// 5. Нажмите "Найти записи"
```

### Найти активные записи определенной категории
```json
{
  "schema": "public",
  "table": "data_records", 
  "filters": {
    "category": "test",
    "is_active": true
  }
}
```

### Работа с пользовательскими таблицами
```sql
-- Создайте свою таблицу
CREATE TABLE custom_table (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  code VARCHAR(50),
  status BOOLEAN DEFAULT true
);

-- Вставьте данные
INSERT INTO custom_table (name, code, status) VALUES 
('Элемент 1', 'CODE123', true),
('Элемент 2', 'CODE456', false);
```

Затем используйте API для поиска:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"schema": "public", "table": "custom_table", "filters": {"code": "CODE123"}}' \
     http://localhost:5000/api/db/search
```