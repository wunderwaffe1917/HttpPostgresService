from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from auth import require_auth, validate_json_input
from models import DataRecord, db
import logging

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# Health check endpoint (no auth required)
@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 503

# GET /api/records - Get all records
@api_bp.route('/records', methods=['GET'])
@require_auth
def get_records():
    """Get all data records with optional filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Max 100 per page
        category = request.args.get('category')
        is_active = request.args.get('is_active', type=bool)
        wiki_id = request.args.get('wiki_id', type=int)
        unit_id = request.args.get('unit_id', type=int)
        
        # Build query
        query = DataRecord.query
        
        if category:
            query = query.filter(DataRecord.category == category)
        
        if is_active is not None:
            query = query.filter(DataRecord.is_active == is_active)
            
        if wiki_id is not None:
            query = query.filter(DataRecord.wiki_id == wiki_id)
            
        if unit_id is not None:
            query = query.filter(DataRecord.unit_id == unit_id)
        
        # Order by creation date (newest first)
        query = query.order_by(DataRecord.created_at.desc())
        
        # Paginate
        records = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'records': [record.to_dict() for record in records.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': records.total,
                'pages': records.pages,
                'has_next': records.has_next,
                'has_prev': records.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting records: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve records',
            'message': str(e)
        }), 500

# GET /api/records/<id> - Get specific record
@api_bp.route('/records/<int:record_id>', methods=['GET'])
@require_auth
def get_record(record_id):
    """Get a specific record by ID"""
    try:
        record = DataRecord.query.get(record_id)
        if not record:
            return jsonify({
                'error': 'Record not found',
                'message': f'No record found with ID {record_id}'
            }), 404
        
        return jsonify({'record': record.to_dict()})
        
    except Exception as e:
        current_app.logger.error(f"Error getting record {record_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve record',
            'message': str(e)
        }), 500

# POST /api/records - Create new record
@api_bp.route('/records', methods=['POST'])
@require_auth
@validate_json_input(required_fields=['title'])
def create_record():
    """Create a new data record"""
    try:
        data = request.get_json()
        
        # Validate input
        title = data.get('title', '').strip()
        if not title:
            return jsonify({
                'error': 'Title cannot be empty'
            }), 400
        
        if len(title) > 200:
            return jsonify({
                'error': 'Title too long',
                'message': 'Title must be 200 characters or less'
            }), 400
        
        # Create record
        record = DataRecord(
            wiki_id=data.get('wiki_id'),
            unit_id=data.get('unit_id'),
            title=title,
            content=data.get('content', ''),
            category=data.get('category'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(record)
        db.session.commit()
        
        current_app.logger.info(f"Created record {record.id}: {record.title}")
        
        return jsonify({
            'message': 'Record created successfully',
            'record': record.to_dict()
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error creating record: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': 'Failed to create record due to database error'
        }), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating record: {str(e)}")
        return jsonify({
            'error': 'Failed to create record',
            'message': str(e)
        }), 500

# PUT /api/records/<id> - Update record
@api_bp.route('/records/<int:record_id>', methods=['PUT'])
@require_auth
@validate_json_input()
def update_record(record_id):
    """Update an existing record"""
    try:
        record = DataRecord.query.get(record_id)
        if not record:
            return jsonify({
                'error': 'Record not found',
                'message': f'No record found with ID {record_id}'
            }), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'wiki_id' in data:
            record.wiki_id = data['wiki_id']
            
        if 'unit_id' in data:
            record.unit_id = data['unit_id']
            
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({
                    'error': 'Title cannot be empty'
                }), 400
            if len(title) > 200:
                return jsonify({
                    'error': 'Title too long',
                    'message': 'Title must be 200 characters or less'
                }), 400
            record.title = title
        
        if 'content' in data:
            record.content = data['content']
        
        if 'category' in data:
            record.category = data['category']
        
        if 'is_active' in data:
            record.is_active = data['is_active']
        
        db.session.commit()
        
        current_app.logger.info(f"Updated record {record.id}: {record.title}")
        
        return jsonify({
            'message': 'Record updated successfully',
            'record': record.to_dict()
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error updating record {record_id}: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': 'Failed to update record due to database error'
        }), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating record {record_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to update record',
            'message': str(e)
        }), 500

# DELETE /api/records/<id> - Delete record
@api_bp.route('/records/<int:record_id>', methods=['DELETE'])
@require_auth
def delete_record(record_id):
    """Delete a record"""
    try:
        record = DataRecord.query.get(record_id)
        if not record:
            return jsonify({
                'error': 'Record not found',
                'message': f'No record found with ID {record_id}'
            }), 404
        
        # Store record info for logging
        record_title = record.title
        
        db.session.delete(record)
        db.session.commit()
        
        current_app.logger.info(f"Deleted record {record_id}: {record_title}")
        
        return jsonify({
            'message': 'Record deleted successfully'
        })
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting record {record_id}: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': 'Failed to delete record due to database error'
        }), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting record {record_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to delete record',
            'message': str(e)
        }), 500

# GET /api/records/by-wiki/<wiki_id> - Get records by wiki_id
@api_bp.route('/records/by-wiki/<int:wiki_id>', methods=['GET'])
@require_auth
def get_records_by_wiki(wiki_id):
    """Get all records for a specific wiki_id"""
    try:
        # Get query parameters for pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Query records by wiki_id
        query = DataRecord.query.filter(DataRecord.wiki_id == wiki_id)
        query = query.order_by(DataRecord.created_at.desc())
        
        # Paginate
        records = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'wiki_id': wiki_id,
            'records': [record.to_dict() for record in records.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': records.total,
                'pages': records.pages,
                'has_next': records.has_next,
                'has_prev': records.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting records for wiki_id {wiki_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve records',
            'message': str(e)
        }), 500

# GET /api/records/by-unit/<unit_id> - Get records by unit_id
@api_bp.route('/records/by-unit/<int:unit_id>', methods=['GET'])
@require_auth
def get_records_by_unit(unit_id):
    """Get all records for a specific unit_id"""
    try:
        # Get query parameters for pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Query records by unit_id
        query = DataRecord.query.filter(DataRecord.unit_id == unit_id)
        query = query.order_by(DataRecord.created_at.desc())
        
        # Paginate
        records = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'unit_id': unit_id,
            'records': [record.to_dict() for record in records.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': records.total,
                'pages': records.pages,
                'has_next': records.has_next,
                'has_prev': records.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting records for unit_id {unit_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve records',
            'message': str(e)
        }), 500

# POST /api/records/bulk - Bulk operations
@api_bp.route('/records/bulk', methods=['POST'])
@require_auth
@validate_json_input(required_fields=['action'])
def bulk_operations():
    """Perform bulk operations on records"""
    try:
        data = request.get_json()
        action = data.get('action')
        record_ids = data.get('record_ids', [])
        
        if not record_ids:
            return jsonify({
                'error': 'No record IDs provided'
            }), 400
        
        if action == 'delete':
            # Bulk delete
            deleted_count = DataRecord.query.filter(DataRecord.id.in_(record_ids)).delete(synchronize_session=False)
            db.session.commit()
            
            current_app.logger.info(f"Bulk deleted {deleted_count} records")
            
            return jsonify({
                'message': f'Successfully deleted {deleted_count} records'
            })
        
        elif action == 'activate':
            # Bulk activate
            updated_count = DataRecord.query.filter(DataRecord.id.in_(record_ids)).update(
                {DataRecord.is_active: True}, synchronize_session=False
            )
            db.session.commit()
            
            current_app.logger.info(f"Bulk activated {updated_count} records")
            
            return jsonify({
                'message': f'Successfully activated {updated_count} records'
            })
        
        elif action == 'deactivate':
            # Bulk deactivate
            updated_count = DataRecord.query.filter(DataRecord.id.in_(record_ids)).update(
                {DataRecord.is_active: False}, synchronize_session=False
            )
            db.session.commit()
            
            current_app.logger.info(f"Bulk deactivated {updated_count} records")
            
            return jsonify({
                'message': f'Successfully deactivated {updated_count} records'
            })
        
        else:
            return jsonify({
                'error': 'Invalid action',
                'message': 'Supported actions: delete, activate, deactivate'
            }), 400
            
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error in bulk operation: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': 'Failed to perform bulk operation due to database error'
        }), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk operation: {str(e)}")
        return jsonify({
            'error': 'Failed to perform bulk operation',
            'message': str(e)
        }), 500
