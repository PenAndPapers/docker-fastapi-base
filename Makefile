.PHONY: docker-up docker-down docker-build docker-logs docker-ps test lint clean install test-all test-cov test-watch test-unit test-integration test-e2e format up-foreground up-background migration migrate-down migrate-logs migrate-check down down-v scaffold-module

# Docker commands
docker-up-foreground:
	docker-compose up

docker-up-background:
	docker-compose up -d

docker-up: docker-up-background  # Alias for docker-up-background for backward compatibility

docker-down:
	docker-compose down --remove-orphans

docker-down-v:
	docker-compose down -v --remove-orphans

docker-build:
	docker-compose build --parallel --no-cache

docker-logs:
	docker-compose logs -f

docker-ps:
	docker-compose ps

# Development commands
install:
	pip install uv
	uv pip install -r requirements.in

# Update dependencies
update-deps:
	uv pip install -r requirements.in
	$(MAKE) docker-build

# Testing commands
test:
	docker-compose exec api pytest

test-unit:
	docker-compose exec api pytest tests/unit -v

test-integration:
	docker-compose exec api pytest tests/integration -v

test-e2e:
	docker-compose exec api pytest tests/e2e -v

test-all:
	docker-compose exec api pytest -v -s

test-cov:
	docker-compose exec api pytest --cov=app --cov-report=term-missing

test-watch:
	docker-compose exec api ptw -- -vv

# Code quality commands
lint:
	docker-compose exec api ruff check . --exclude scaffold/ --exclude .venv/ --exclude "scaffold/*"
	docker-compose exec api black --check . --exclude "scaffold/" --exclude ".venv/" --exclude "scaffold/*"

format:
	docker-compose exec -T api ruff check --fix . --exclude scaffold/ --exclude .venv/ --exclude "scaffold/*" --exclude ".venv/*"
	docker-compose exec -T api black . --exclude "scaffold/" --exclude ".venv/" --exclude ".venv/*" --exclude "scaffold/*"

# Migration commands
migration:
	@read -p "Enter migration name: " name; \
	timestamp=$$(date +%Y%m%d_%H%M%S); \
	docker-compose exec api alembic revision --autogenerate -m "$$name"

migrate:
	docker-compose exec api alembic upgrade head

migrate-down:
	docker-compose exec api alembic downgrade -1

migrate-logs:
	docker-compose exec api alembic history --verbose

migrate-check:
	docker-compose exec api alembic current
	@echo "\nPending migrations:"
	docker-compose exec api alembic heads

# Module scaffolding command
scaffold-module:
	@echo "Starting scaffold-module..."
	@read -p "Enter module name, must be singular: " name; \
	if [ -z "$$name" ]; then \
		echo "Error: Module name cannot be empty"; \
		exit 1; \
	fi; \
	module_lower="$$(echo "$$name" | tr '[:upper:]' '[:lower:]')"; \
	module_upper="$$(echo "$$module_lower" | perl -pe 's/(^|_)([a-z])/\U\2/g; s/_//g')"; \
	module_path="app/modules/$$module_lower"; \
	test_unit_path="tests/unit/$$module_lower"; \
	test_e2e_path="tests/e2e/$$module_lower"; \
	test_integration_path="tests/integration/$$module_lower"; \
	\
	echo "Creating module: $$module_lower"; \
	echo "Module path: $$module_path"; \
	\
	if [ -d "$$module_path" ]; then \
		echo "Error: Module $$module_lower already exists"; \
		exit 1; \
	fi; \
	\
	echo "Copying module scaffold..."; \
	cp -r scaffold/module "$$module_path" || { echo "Error: Failed to copy scaffold/module"; exit 1; }; \
	\
	echo "Renaming and replacing placeholders in module files..."; \
	find "$$module_path" -type f -name "*.py" | while read -r file; do \
		new_name="$$(echo "$$file" | sed "s/{Module}/$$module_upper/")"; \
		mv "$$file" "$$new_name" || { echo "Error: Failed to rename $$file"; exit 1; }; \
		perl -pi -e "s/{Module}/$$module_upper/g; s/{module}/$$module_lower/g" "$$new_name" || { echo "Error: Failed to replace placeholders in $$new_name"; exit 1; }; \
		echo "Processed: $$new_name"; \
	done; \
	\
	echo "Creating test directories..."; \
	mkdir -p "$$test_unit_path" "$$test_e2e_path" "$$test_integration_path" || { echo "Error: Failed to create test directories"; exit 1; }; \
	\
	if [ ! -f "scaffold/test/test_{module}.py" ]; then \
		echo "Error: Test template scaffold/test/test_{module}.py not found!"; \
		exit 1; \
	fi; \
	\
	echo "Copying test files..."; \
	for dir in "$$test_unit_path" "$$test_e2e_path" "$$test_integration_path"; do \
		test_file="$$dir/test_$$module_lower.py"; \
		cp scaffold/test/test_{module}.py "$$test_file" || { echo "Error: Failed to copy test file"; exit 1; }; \
		perl -pi -e "s/{module}/$$module_lower/g" "$$test_file" || { echo "Error: Failed to replace placeholders in $$test_file"; exit 1; }; \
		echo "Created test file: $$test_file"; \
	done; \
	\
	echo "Module $$name created successfully at $$module_path"


# Cleanup commands
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Help command
help:
	@echo "Available commands:"
	@echo "  up-foreground   - Start the application in foreground mode"
	@echo "  up-background   - Start the application in background mode"
	@echo "  up              - Alias for up-background"
	@echo "  down            - Stop the application"
	@echo "  down-v          - Stop the application and remove volumes"
	@echo "  docker-build    - Build the containers"
	@echo "  docker-logs     - View application logs"
	@echo "  docker-ps       - List running containers"
	@echo "  install         - Install dependencies using uv"
	@echo "  update-deps     - Update dependencies"
	@echo "  test            - Run all tests"
	@echo "  test-unit       - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-e2e        - Run end-to-end tests"
	@echo "  test-all        - Run tests with verbose output"
	@echo "  test-cov        - Run tests with coverage report"
	@echo "  test-watch      - Run tests in watch mode"
	@echo "  lint            - Run linting checks"
	@echo "  format          - Format code using ruff and black"
	@echo "  migration       - Create a new migration file"
	@echo "  migrate         - Run all pending migrations"
	@echo "  scaffold-module - Generate a new module"
