# Getting Started Guide

## Prerequisites
- Docker and Docker Compose installed
- Make (optional, but recommended)
- Git

## Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:
```env
# API
API_PORT=8000

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_PORT=5432

# Redis
REDIS_PORT=6379
```

## Starting the Application

### Using Make (Recommended)

1. Build the containers:
```bash
make docker-build
```

2. Start the application:
```bash
make docker-up
```

3. Run database migrations:
```bash
make migrate
```

### Stopping the Application

1. Stop containers (keeps data):
```bash
make docker-down
```

2. Stop containers and remove volumes (fresh start):
```bash
make docker-down-v
```

### Development Commands

```bash
# Docker Operations
make docker-build      # Build containers
make docker-up         # Start containers
make docker-down       # Stop containers (keep data)
make docker-down-v     # Stop containers and remove volumes
make docker-logs       # View logs

# Code Quality
make format           # Format code using black
make clean            # Clean up python cache files
make lint            # Run linting checks

# Database Operations
make migration        # Create new migration
make migrate         # Apply migrations
make migrate-down    # Rollback last migration
make migrate-check   # Check migration status
make migrate-logs    # View migration history

# Testing (if implemented)
make test            # Run all tests
make test-cov        # Run tests with coverage
```

### Code Formatting∏

To maintain code quality:

1. Format code before committing:
```bash
make format
```

2. Clean up cache files:
```bash
make clean
```

3. Run linting checks:
```bash
make lint
```

It's recommended to run these commands before committing changes to ensure code consistency.

### Using Docker Compose Directly

1. Build the containers:
```bash
docker-compose build
```

2. Start the application:
```bash
docker-compose up -d
```

3. Run migrations:
```bash
docker-compose exec api alembic upgrade head
```

## Verify Installation

1. Check if services are running:
```bash
docker-compose ps
```

2. Test the API:
```bash
# Health check
curl http://localhost:8000/health

# Create a todo
curl -X POST http://localhost:8000/todo \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Todo", "description": "Testing the API", "severity": "LOW"}'
```

## Development Commands

### Docker Operations
```bash
# Start services
make up

# Stop services (keep data)
make docker-down

# Stop services and remove volumes
make docker-down-v

# View logs
make logs
```

### Database Operations
```bash
# Create new migration
make migration

# Apply migrations
make migrate

# Rollback last migration
make migrate-down

# Check migration status
make migrate-check
```

## Project Structure
See [Project Structure](project_structure.md) for detailed information about the codebase organization.

## Database Migrations
See [Migrations Guide](migrations.md) for detailed information about database migrations.

## Common Issues

### Port Conflicts
If you see port conflicts:
1. Check if ports 8000, 5432, or 6379 are in use
2. Modify the ports in `.env` file
3. Restart the application

### Database Connection Issues
If the API can't connect to the database:
1. Ensure database container is running
2. Check database credentials in `.env`
3. Wait a few seconds for database to initialize
4. Check database logs: `docker-compose logs db`

### Permission Issues
If you encounter permission issues:
1. Check the user ID in docker-compose.yml
2. Ensure proper file permissions in mounted volumes
3. Try running commands with sudo if needed

## Next Steps
1. Explore the API documentation at `http://localhost:8000/docs`
2. Review the project structure
3. Set up your development environment
4. Start building new features!

## Additional Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/) 