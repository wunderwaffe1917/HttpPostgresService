from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from auth import require_auth, validate_json_input
from models import DatabaseManager
import logging

# Create blueprint for dynamic database operations
dynamic_bp = Blueprint('dynamic', __name__, url_prefix='/api/db')

@dynamic_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@dynamic_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# GET /api/db/schemas - Получить список схем
@dynamic_bp.route('/schemas', methods=['GET'])
@require_auth
def get_schemas():
    """Получить список схем в базе данных"""
    try:
        schemas = DatabaseManager.get_schemas()
        return jsonify({
            'schemas': schemas,
            'count': len(schemas)
        })
    except Exception as e:
        current_app.logger.error(f"Error getting schemas: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve schemas',
            'message': str(e)
        }), 500

# GET /api/db/schemas/<schema>/tables - Получить список таблиц в схеме
@dynamic_bp.route('/schemas/<schema_name>/tables', methods=['GET'])
@require_auth
def get_tables(schema_name):
    """Получить список таблиц в схеме"""
    try:
        tables = DatabaseManager.get_tables(schema_name)
        return jsonify({
            'schema': schema_name,
            'tables': tables,
            'count': len(tables)
        })
    except Exception as e:
        current_app.logger.error(f"Error getting tables for schema {schema_name}: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve tables',
            'message': str(e)
        }), 500

# GET /api/db/schemas/<schema>/tables/<table>/columns - Получить колонки таблицы
@dynamic_bp.route('/schemas/<schema_name>/tables/<table_name>/columns', methods=['GET'])
@require_auth
def get_table_columns(schema_name, table_name):
    """Получить информацию о колонках таблицы"""
    try:
        columns = DatabaseManager.get_table_columns(table_name, schema_name)
        return jsonify({
            'schema': schema_name,
            'table': table_name,
            'columns': columns,
            'count': len(columns)
        })
    except Exception as e:
        current_app.logger.error(f"Error getting columns for {schema_name}.{table_name}: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve table columns',
            'message': str(e)
        }), 500

# GET /api/db/schemas/<schema>/tables/<table>/data - Получить данные из таблицы
@dynamic_bp.route('/schemas/<schema_name>/tables/<table_name>/data', methods=['GET'])
@require_auth
def get_table_data(schema_name, table_name):
    """Получить данные из таблицы с возможностью фильтрации"""
    try:
        # Получаем параметры запроса
        limit = min(int(request.args.get('limit', 100)), 1000)  # Максимум 1000 записей
        offset = int(request.args.get('offset', 0))
        
        # Получаем фильтры из query параметров
        filters = {}
        for key, value in request.args.items():
            if key not in ['limit', 'offset']:
                filters[key] = value
        
        # Если нет фильтров из query параметров, проверяем тело запроса
        if not filters and request.is_json:
            data = request.get_json()
            if data and 'filters' in data:
                filters = data['filters']
        
        result = DatabaseManager.execute_select(
            table_name=table_name,
            schema_name=schema_name,
            filters=filters if filters else None,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'schema': schema_name,
            'table': table_name,
            'filters': filters,
            'limit': limit,
            'offset': offset,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting data from {schema_name}.{table_name}: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve table data',
            'message': str(e)
        }), 500

# POST /api/db/schemas/<schema>/tables/<table>/data - Вставить данные в таблицу
@dynamic_bp.route('/schemas/<schema_name>/tables/<table_name>/data', methods=['POST'])
@require_auth
@validate_json_input()
def insert_table_data(schema_name, table_name):
    """Вставить новые данные в таблицу"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'error': 'Missing data field',
                'message': 'Request must contain "data" field with record data'
            }), 400
        
        record_data = data['data']
        
        result = DatabaseManager.execute_insert(
            table_name=table_name,
            data=record_data,
            schema_name=schema_name
        )
        
        return jsonify({
            'message': 'Data inserted successfully',
            'schema': schema_name,
            'table': table_name,
            'inserted_data': result
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error inserting data into {schema_name}.{table_name}: {str(e)}")
        return jsonify({
            'error': 'Failed to insert data',
            'message': str(e)
        }), 500

# PUT /api/db/schemas/<schema>/tables/<table>/data - Обновить данные в таблице
@dynamic_bp.route('/schemas/<schema_name>/tables/<table_name>/data', methods=['PUT'])
@require_auth
@validate_json_input()
def update_table_data(schema_name, table_name):
    """Обновить данные в таблице"""
    try:
        data = request.get_json()
        
        if 'data' not in data or 'filters' not in data:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Request must contain "data" and "filters" fields'
            }), 400
        
        update_data = data['data']
        filters = data['filters']
        
        result = DatabaseManager.execute_update(
            table_name=table_name,
            data=update_data,
            filters=filters,
            schema_name=schema_name
        )
        
        return jsonify({
            'message': 'Data updated successfully',
            'schema': schema_name,
            'table': table_name,
            'updated_records': len(result),
            'updated_data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating data in {schema_name}.{table_name}: {str(e)}")
        return jsonify({
            'error': 'Failed to update data',
            'message': str(e)
        }), 500

# DELETE /api/db/schemas/<schema>/tables/<table>/data - Удалить данные из таблицы
@dynamic_bp.route('/schemas/<schema_name>/tables/<table_name>/data', methods=['DELETE'])
@require_auth
@validate_json_input()
def delete_table_data(schema_name, table_name):
    """Удалить данные из таблицы"""
    try:
        data = request.get_json()
        
        if 'filters' not in data:
            return jsonify({
                'error': 'Missing filters field',
                'message': 'Request must contain "filters" field to specify which records to delete'
            }), 400
        
        filters = data['filters']
        
        deleted_count = DatabaseManager.execute_delete(
            table_name=table_name,
            filters=filters,
            schema_name=schema_name
        )
        
        return jsonify({
            'message': 'Data deleted successfully',
            'schema': schema_name,
            'table': table_name,
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting data from {schema_name}.{table_name}: {str(e)}")
        return jsonify({
            'error': 'Failed to delete data',
            'message': str(e)
        }), 500

# POST /api/db/search - Универсальный поиск по таблицам
@dynamic_bp.route('/search', methods=['POST'])
@require_auth
@validate_json_input()
def universal_search():
    """Универсальный поиск по таблицам с гибкими фильтрами"""
    try:
        data = request.get_json()
        
        required_fields = ['schema', 'table']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        schema_name = data['schema']
        table_name = data['table']
        filters = data.get('filters', {})
        limit = min(int(data.get('limit', 100)), 1000)
        offset = int(data.get('offset', 0))
        
        result = DatabaseManager.execute_select(
            table_name=table_name,
            schema_name=schema_name,
            filters=filters if filters else None,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'message': 'Search completed successfully',
            'search_params': {
                'schema': schema_name,
                'table': table_name,
                'filters': filters,
                'limit': limit,
                'offset': offset
            },
            'results': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in universal search: {str(e)}")
        return jsonify({
            'error': 'Search failed',
            'message': str(e)
        }), 500