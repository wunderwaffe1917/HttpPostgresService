# Flask API Service

## Overview

This is a RESTful API service built with Flask that provides authenticated access to a PostgreSQL database. The application implements Bearer token authentication using JWT and offers CRUD operations for data records through a clean API interface.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based Bearer token authentication
- **API Design**: RESTful endpoints with JSON responses
- **Error Handling**: Centralized error handling with appropriate HTTP status codes

### Frontend Architecture
- **Technology**: Vanilla JavaScript with Bootstrap 5
- **Theme**: Dark theme optimized for development
- **Purpose**: API documentation and testing interface

## Key Components

### Core Application Components
1. **app.py**: Main Flask application factory with database initialization
2. **models.py**: SQLAlchemy models and DatabaseManager for dynamic operations
3. **auth.py**: JWT authentication system with token generation/validation
4. **api_routes.py**: RESTful API endpoints with authentication decorators
5. **dynamic_routes.py**: Dynamic database operations with schema/table selection
6. **main.py**: Application entry point

### Database Models
1. **ApiToken**: Manages API authentication tokens with lifecycle tracking
2. **DataRecord**: Enhanced model with id_template field for search examples
3. **DatabaseManager**: Static class for dynamic database operations across schemas/tables

### Authentication System
- JWT tokens with HS256 encryption
- Bearer token authentication via Authorization header
- Token-based access control with decorator pattern
- Admin token auto-creation for initial setup

### Dynamic Database Features
- **Schema browsing**: List all available database schemas
- **Table discovery**: Explore tables within any schema
- **Column inspection**: View detailed column information and data types
- **Flexible search**: Find records by any column value or multiple filters
- **CRUD operations**: Insert, update, delete data in any table
- **Universal search endpoint**: Single API for complex queries

## Data Flow

1. **Authentication Flow**:
   - Client requests include Bearer token in Authorization header
   - JWT tokens are validated and decoded for each request
   - Invalid/missing tokens return 401 Unauthorized responses

2. **API Request Flow**:
   - Requests hit Flask blueprint routes (`/api/*`)
   - Authentication decorator validates tokens
   - Business logic processes the request
   - JSON responses with appropriate HTTP status codes

3. **Database Interaction**:
   - SQLAlchemy ORM handles database operations
   - Connection pooling with health checks
   - Automatic table creation on application startup

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and request handling
- **SQLAlchemy**: Database ORM and connection management
- **PyJWT**: JWT token generation and validation
- **Flask-CORS**: Cross-origin request handling
- **psycopg2**: PostgreSQL database adapter

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: Client-side API interaction

## Deployment Strategy

### Environment Configuration
- Database URL via `DATABASE_URL` environment variable
- JWT secret key via `JWT_SECRET_KEY` environment variable
- Session secret via `SESSION_SECRET` environment variable
- Default development values provided for local testing

### Database Setup
- Automatic table creation on application startup
- PostgreSQL connection with connection pooling
- Health check endpoint for monitoring database connectivity

### Docker Deployment
- **Dockerfile**: Multi-stage build with Python 3.11-slim base image
- **docker-compose.yml**: Complete stack with PostgreSQL database
- **Health checks**: Automated container health monitoring
- **Entrypoint script**: Database readiness checking before app start
- **Non-root user**: Security-focused container configuration

### Docker Files Structure
- `Dockerfile` - Container build configuration
- `docker-compose.yml` - Multi-service orchestration
- `entrypoint.sh` - Container startup script
- `.dockerignore` - Build context optimization
- `.env.example` - Environment variables template
- `docker-run.sh` - Quick deployment script
- `test-api.sh` - API testing automation

### Production Considerations
- ProxyFix middleware for reverse proxy deployments
- Connection pool management with pre-ping health checks
- Comprehensive logging configuration
- CORS configuration for cross-origin requests
- Container orchestration with health checks
- Automated database initialization and migrations

## Changelog
- June 29, 2025: Initial Flask API setup with PostgreSQL and JWT authentication
- June 29, 2025: Added Docker containerization with complete deployment stack

## Recent Changes
- ✅ Fixed health check endpoint SQL query compatibility
- ✅ Created complete Docker deployment configuration
- ✅ Added Dockerfile with Python 3.11 and security best practices
- ✅ Implemented docker-compose.yml with PostgreSQL service
- ✅ Created deployment automation scripts (docker-run.sh, test-api.sh)
- ✅ Added comprehensive documentation and examples
- ✅ Implemented dynamic database API with schema/table selection
- ✅ Added flexible search by any column values with multiple filters
- ✅ Created web interface for dynamic database operations (/dynamic)
- ✅ Added DatabaseManager class for universal database operations
- ✅ Enhanced DataRecord model with id_template field for search examples

## User Preferences

Preferred communication style: Simple, everyday language.