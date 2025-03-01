# Project Structure

## Overview
This project follows a modular, clean architecture pattern with clear separation of concerns. Each module is self-contained with its own components for different responsibilities.

## Directory Structure

```
.
├── app/                                # Main application directory
│   ├── config.py
│   ├── main.py
│   ├── core/                           # Core components
│   │   └── exceptions.py               # Custom exceptions
│   │   └── pagination.py               # Pagination models
│   │
│   ├── database/                       # Database connection and session management
│   |   └── session.py                  # Database session management    
│   |   └── helper.py                   # Database helper functions  
│   │
│   └── modules/                        # Modules - groups related features
│   │    └── todo/
│   │     │
│   │     ├── constants/                # Constants for the todo module
│   │     │   └── enums.py
│   │     │
│   │     ├── model/                    # Database models/entities, defines table structure
│   │     │   └── TodoModel.py
│   │     │
│   │     ├── providers/                # Dependency injection, service locator
│   │     │   └── services.py           # Database connection and session management, Service factory and dependency wiring
│   │     │
│   │     ├── repository/               # Data access layer, handles database operations, business logic
│   │     │   └── TodoRepository.py
│   │     │
│   │     ├── schema/                   # Pydantic models for request/response validation
│   │     │   └── TodoSchema.py
│   │     │
│   │     ├── service/                  # Core business logic layer:
│   │     │   └── TodoService.py        #  - Implements domain rules and workflows
│   │     │                             #  - Processes and validates business data
│   │     │                             #  - Coordinates complex operations
│   │     │                             #  - Independent of API/presentation concerns
│   │     │
│   │     └── router.py                 # FastAPI route definitions and endpoint handlers
│   │
│   └── utils/                          # General utility functions
│
├── docker                              # Docker configuration  
│   ├── api/
│   │   └── Dockerfile
│   |
│   ├── postgres/
│   │   ├── versions/
│   │   ├── Dockerfile
│   │   └── init.sql
│   |
│   └── redis/
│       └── Dockerfile
|
├── docs/                               # Project documentation
|
├── scaffold/
│       ├── module                      # Module scaffolding
│       └── test                        # Test scaffolding
|
├── tests/                              # Test files
│   ├── __init__.py
│   ├── conftest.py
│   ├── e2e/
│   │   ├── __init__.py
│   │   └── test_todo_api.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_todo_service.py
│   │
│   └── unit/
│       ├── __init__.py
│       └── test_todo_controller.py
|
├── docker-compose.yml
├── requirements.in
├── pytest.ini
├── Makefile
├── .dockerignore
├── .gitignore
└── .env 
```

## Component Responsibilities

### Models (`model/`)
- Define database table structures
- Handle database relationships
- Example: `TodoModel.py` defines the Todo table structure

### Schemas (`schema/`)
- Define request/response data shapes
- Handle data validation
- Convert between API and internal representations

### Services (`service/`)
- Implement business logic
- Handle status transitions
- Validate business rules
- Orchestrate data operations

### Repositories (`repository/`)
- Handle database operations
- Implement data access patterns
- No business logic
- Pure database interactions

### Providers (`providers/`)
- Handle dependency injection
- Wire up services and repositories
- Manage component lifecycle

### Router (`router.py`)
- Define API endpoints
- Handle request routing
- Basic request validation

## Data Flow
HTTP Request → Router → Controller → Service → Repository → Database

## Key Design Principles
1. **Separation of Concerns**
   - Each component has a single responsibility
   - Clear boundaries between layers

2. **Dependency Injection**
   - Components receive their dependencies
   - Easier testing and maintenance

3. **Clean Architecture**
   - Independent of frameworks
   - Testable business logic
   - Isolated database operations 