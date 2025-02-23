# Database Migrations Guide

## Overview
This project uses Alembic for database migrations. Migrations help track and version database schema changes.

## Commands

### Create a New Migration
```bash
# Create a new migration file
make migration
# Enter descriptive name when prompted (e.g., "create_todos_table")
```

### Apply Migrations
```bash
# Apply all pending migrations
make migrate
```

### Rollback Migrations
```bash
# Rollback the last migration
make migrate-down
```

### Check Migration Status
```bash
# View migration history
make migrate-logs

# Check current and pending migrations
make migrate-check
```

## Migration File Structure
Migrations are stored in `docker/postgres/migrations/versions/`. Each migration file contains:

```python
"""migration description

Revision ID: abc123
Revises: previous_revision
Create Date: YYYY-MM-DD HH:MM:SS
"""

def upgrade():
    # Changes to apply when migrating up
    pass

def downgrade():
    # Changes to apply when rolling back
    pass
```

## Best Practices

1. **Naming Migrations**
   - Use descriptive names (e.g., "create_user_table", "add_email_column")
   - Include the purpose of the change

2. **Testing Migrations**
   - Test both upgrade and downgrade
   - Verify data integrity after migration
   - Test with representative data

3. **Writing Migrations**
   - One logical change per migration
   - Include both upgrade and downgrade steps
   - Comment complex SQL operations

4. **Running Migrations**
   - Always backup database before migrating
   - Run migrations during low-traffic periods
   - Test migrations in development first

## Common Issues

### Migration Conflicts
If you get revision conflicts:
```bash
# Check current revision
make migrate-check

# Manually update revision in migration file
# Edit: down_revision = 'correct_previous_revision'
```

### Failed Migrations
If a migration fails:
1. Check the error message
2. Rollback to last good state: `make migrate-down`
3. Fix the migration file
4. Try again: `make migrate`

## Example Migration

```python
"""create todos table

Revision ID: create_todos_table
Create Date: 2024-02-01 14:57:45
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('status', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('todos')
```

## Additional Resources
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/) 