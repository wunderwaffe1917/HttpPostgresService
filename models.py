from app import db
from datetime import datetime
from sqlalchemy import Text, Boolean, Integer, String, DateTime, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import json

class ApiToken(db.Model):
    """Model for storing API tokens"""
    __tablename__ = 'api_tokens'
    
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    token = db.Column(Text, nullable=False)
    is_active = db.Column(Boolean, default=True, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    last_used = db.Column(DateTime)
    
    def __repr__(self):
        return f'<ApiToken {self.name}>'

class DataRecord(db.Model):
    """Generic model for storing data records"""
    __tablename__ = 'data_records'
    
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(200), nullable=False)
    content = db.Column(Text)
    category = db.Column(String(100))
    id_template = db.Column(String(100))  # Добавляем поле для примера поиска
    is_active = db.Column(Boolean, default=True, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'id_template': self.id_template,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DataRecord {self.title}>'

class DatabaseManager:
    """Класс для динамической работы с базой данных"""
    
    @staticmethod
    def get_schemas():
        """Получить список схем в базе данных"""
        try:
            result = db.session.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schema_name
            """))
            return [row[0] for row in result]
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения схем: {str(e)}")
    
    @staticmethod
    def get_tables(schema_name='public'):
        """Получить список таблиц в схеме"""
        try:
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = :schema_name
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """), {'schema_name': schema_name})
            return [row[0] for row in result]
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения таблиц: {str(e)}")
    
    @staticmethod
    def get_table_columns(table_name, schema_name='public'):
        """Получить информацию о колонках таблицы"""
        try:
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = :schema_name 
                AND table_name = :table_name
                ORDER BY ordinal_position
            """), {'schema_name': schema_name, 'table_name': table_name})
            
            columns = []
            for row in result:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3]
                })
            return columns
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка получения колонок: {str(e)}")
    
    @staticmethod
    def execute_select(table_name, schema_name='public', filters=None, limit=100, offset=0):
        """Выполнить SELECT запрос с фильтрами"""
        try:
            # Проверяем существование таблицы
            table_exists = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = :schema_name 
                    AND table_name = :table_name
                )
            """), {'schema_name': schema_name, 'table_name': table_name}).scalar()
            
            if not table_exists:
                raise Exception(f"Таблица {schema_name}.{table_name} не существует")
            
            # Строим базовый запрос
            query = f'SELECT * FROM "{schema_name}"."{table_name}"'
            params = {}
            
            # Добавляем фильтры
            if filters:
                where_conditions = []
                for i, (column, value) in enumerate(filters.items()):
                    param_name = f'filter_{i}'
                    where_conditions.append(f'"{column}" = :{param_name}')
                    params[param_name] = value
                
                if where_conditions:
                    query += ' WHERE ' + ' AND '.join(where_conditions)
            
            # Добавляем LIMIT и OFFSET
            query += f' LIMIT {limit} OFFSET {offset}'
            
            result = db.session.execute(text(query), params)
            
            # Получаем названия колонок
            columns = [col for col in result.keys()]
            
            # Получаем данные
            rows = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Преобразуем datetime в строку
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[col] = value
                rows.append(row_dict)
            
            return {
                'columns': columns,
                'rows': rows,
                'count': len(rows)
            }
            
        except SQLAlchemyError as e:
            raise Exception(f"Ошибка выполнения запроса: {str(e)}")
    
    @staticmethod
    def execute_insert(table_name, data, schema_name='public'):
        """Выполнить INSERT запрос"""
        try:
            # Проверяем существование таблицы
            table_exists = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = :schema_name 
                    AND table_name = :table_name
                )
            """), {'schema_name': schema_name, 'table_name': table_name}).scalar()
            
            if not table_exists:
                raise Exception(f"Таблица {schema_name}.{table_name} не существует")
            
            if not data:
                raise Exception("Данные для вставки не предоставлены")
            
            # Строим INSERT запрос
            columns = list(data.keys())
            placeholders = [f':{col}' for col in columns]
            
            query = f'''
                INSERT INTO "{schema_name}"."{table_name}" ({", ".join(f'"{col}"' for col in columns)})
                VALUES ({", ".join(placeholders)})
                RETURNING *
            '''
            
            result = db.session.execute(text(query), data)
            db.session.commit()
            
            # Возвращаем вставленную запись
            row = result.fetchone()
            if row:
                row_dict = {}
                for i, col in enumerate(result.keys()):
                    value = row[i]
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[col] = value
                return row_dict
            
            return None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Ошибка вставки данных: {str(e)}")
    
    @staticmethod
    def execute_update(table_name, data, filters, schema_name='public'):
        """Выполнить UPDATE запрос"""
        try:
            if not data:
                raise Exception("Данные для обновления не предоставлены")
            
            if not filters:
                raise Exception("Фильтры для обновления не предоставлены")
            
            # Строим UPDATE запрос
            set_clauses = []
            params = {}
            
            # SET часть
            for i, (column, value) in enumerate(data.items()):
                param_name = f'set_{i}'
                set_clauses.append(f'"{column}" = :{param_name}')
                params[param_name] = value
            
            # WHERE часть
            where_conditions = []
            for i, (column, value) in enumerate(filters.items()):
                param_name = f'where_{i}'
                where_conditions.append(f'"{column}" = :{param_name}')
                params[param_name] = value
            
            query = f'''
                UPDATE "{schema_name}"."{table_name}"
                SET {", ".join(set_clauses)}
                WHERE {" AND ".join(where_conditions)}
                RETURNING *
            '''
            
            result = db.session.execute(text(query), params)
            db.session.commit()
            
            # Возвращаем обновленные записи
            rows = []
            for row in result:
                row_dict = {}
                for i, col in enumerate(result.keys()):
                    value = row[i]
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[col] = value
                rows.append(row_dict)
            
            return rows
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Ошибка обновления данных: {str(e)}")
    
    @staticmethod
    def execute_delete(table_name, filters, schema_name='public'):
        """Выполнить DELETE запрос"""
        try:
            if not filters:
                raise Exception("Фильтры для удаления не предоставлены")
            
            # WHERE часть
            where_conditions = []
            params = {}
            for i, (column, value) in enumerate(filters.items()):
                param_name = f'where_{i}'
                where_conditions.append(f'"{column}" = :{param_name}')
                params[param_name] = value
            
            query = f'''
                DELETE FROM "{schema_name}"."{table_name}"
                WHERE {" AND ".join(where_conditions)}
            '''
            
            result = db.session.execute(text(query), params)
            db.session.commit()
            
            # Получаем количество удаленных записей из результата
            return result.rowcount if hasattr(result, 'rowcount') else 0
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Ошибка удаления данных: {str(e)}")
