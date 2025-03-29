.PHONY: docker-up docker-down docker-build docker-logs docker-ps test lint clean install test-all test-cov test-watch test-unit test-integration test-e2e format up-foreground up-background migration migrate-down migrate-logs migrate-check down down-v scaffold-module

# Development commands (local machine)
install:
	pip install uv
	uv pip install -r requirements.in
	uv pip compile requirements.in -o requirements.txt

update-deps:
	uv pip install -r requirements.in
	uv pip compile requirements.in -o requirements.txt
	$(MAKE) docker-build
	@echo "Dependencies updated successfully"

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

docker-restart:
	$(MAKE) docker-down
	$(MAKE) docker-up

docker-build:
	docker-compose build --parallel --no-cache

docker-update-deps:
	docker-compose exec api pip install -r requirements.in
	$(MAKE) docker-build
	@echo "Container dependencies updated successfully"

docker-logs:
	docker-compose logs -f

docker-ps:
	docker-compose ps

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
	docker-compose exec api ruff check app tests docker --exclude .venv --exclude scaffold
	docker-compose exec api black --check app tests docker --exclude .venv --exclude scaffold

format:
	docker-compose exec -T api ruff format app tests docker --exclude .venv --exclude scaffold
	docker-compose exec -T api black app tests docker --exclude .venv --exclude scaffold

# Migration commands
migration:
	@read -p "Enter migration name: " name; \
	docker-compose exec api alembic revision --autogenerate -m "$$name"

migrate:
	docker-compose exec api alembic upgrade head

migrate-down:
	docker-compose exec api alembic downgrade -1

migrate-logs:
	docker-compose exec api alembic history --verbose

migrate-clean:
	@read -p "DANGER: This will remove all migration files! Are you sure you want to delete all migrations? (y/n) " answer; \
	if [ "$$answer" = "y" ]; then \
		docker-compose exec api rm -rf /app/docker/postgres/migrations/__pycache__; \
		docker-compose exec api rm -rf /app/docker/postgres/migrations/versions/*; \
		rm -rf docker/postgres/migrations/__pycache__; \
		rm -rf docker/postgres/migrations/versions/*; \
		echo "Migration files removed"; \
	else \
		echo "Operation cancelled"; \
	fi

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
	@echo "\033[33m Development commands: \033[0m"
	@echo "\033[32m  install                             - Install dependencies using uv \033[0m"
	@echo "\033[32m  update-deps                         - Update dependencies locally and rebuild docker \033[0m"
	@echo ""
	@echo "\033[1;33m Docker commands: \033[0m"
	@echo "\033[32m  docker-up-foreground                - Start the application in foreground mode \033[0m"
	@echo "\033[32m  docker-up-background                - Start the application in background mode \033[0m"
	@echo "\033[32m  docker-up                           - Alias for docker-up-background \033[0m"
	@echo "\033[32m  docker-down                         - Stop the application and remove orphans \033[0m"
	@echo "\033[32m  docker-down-v                       - Stop the application, remove orphans and volumes \033[0m"
	@echo "\033[32m  docker-build                        - Build the containers \033[0m"
	@echo "\033[32m  docker-update-deps                  - Update dependencies in container \033[0m"
	@echo "\033[32m  docker-logs                         - View application logs \033[0m"
	@echo "\033[32m  docker-ps                           - List running containers \033[0m"
	@echo ""
	@echo "\033[1;33m Testing commands: \033[0m"
	@echo "\033[32m  test                                - Run all tests \033[0m"
	@echo "\033[32m  test-unit                           - Run unit tests \033[0m"
	@echo "\033[32m  test-integration                    - Run integration tests \033[0m"
	@echo "\033[32m  test-e2e                            - Run end-to-end tests \033[0m"
	@echo " \033[32m test-all                            - Run tests with verbose output \033[0m"
	@echo "\033[32m  test-cov                            - Run tests with coverage report" \033[0m
	@echo "\033[32m  test-watch                          - Run tests in watch mode \033[0m"
	@echo ""
	@echo "\033[1;33m Code quality commands: \033[0m"
	@echo "\033[32m  lint                                - Run linting checks \033[0m"
	@echo "\033[32m  format                              - Format code using ruff and black \033[0m"
	@echo ""
	@echo "\033[1;33m Migration commands: \033[0m"
	@echo "\033[32m  migration                           - Create a new migration file \033[0m"
	@echo "\033[32m  migrate                             - Run all pending migrations \033[0m"
	@echo "\033[32m  migrate-down                        - Downgrade to previous migration \033[0m"
	@echo "\033[32m  migrate-logs                        - Show migration history \033[0m"
	@echo "\033[32m  migrate-clean                       - Remove all migration files (with confirmation) \033[0m"
	@echo "\033[32m  migrate-check                       - Show current and pending migrations \033[0m"
	@echo ""
	@echo "\033[1;33m Module commands: \033[0m"
	@echo "\033[32m  scaffold-module                     - Generate a new module \033[0m"
	@echo ""
	@echo "\033[1;33m Cleanup commands: \033[0m"
	@echo "\033[32m  clean                               - Remove Python cache and temporary files \033[0m"