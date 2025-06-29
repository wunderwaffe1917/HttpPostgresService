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
2. **models.py**: SQLAlchemy models for ApiToken and DataRecord entities
3. **auth.py**: JWT authentication system with token generation/validation
4. **api_routes.py**: RESTful API endpoints with authentication decorators
5. **main.py**: Application entry point

### Database Models
1. **ApiToken**: Manages API authentication tokens with lifecycle tracking
2. **DataRecord**: Generic data storage model with title, content, and categorization

### Authentication System
- JWT tokens with HS256 encryption
- Bearer token authentication via Authorization header
- Token-based access control with decorator pattern
- Admin token auto-creation for initial setup

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

### Production Considerations
- ProxyFix middleware for reverse proxy deployments
- Connection pool management with pre-ping health checks
- Comprehensive logging configuration
- CORS configuration for cross-origin requests

## Changelog
- June 29, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.