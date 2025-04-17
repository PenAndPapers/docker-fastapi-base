from typing import TypeVar, Type
from sqlalchemy.orm import Session, Query
from pydantic import BaseModel
from app.core.exceptions import DatabaseError, NotFoundError, BadRequestError

ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DatabaseRepository:
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def query(self) -> Query[ModelType]:
        """
        Get a query object for the given model.

        Returns:
            Query object for the given model.

        Raises:
            DatabaseError if the items are not found.
        """
        try:
            return self.db.query(self.model)
        except Exception as e:
            raise DatabaseError(detail=f"Error: {e}")

    def _get_filtered_query(self, filters: dict) -> Query:
        """
        Build a filtered query based on filter criteria

        Args:
            filters: Dictionary of filter criteria.

        Returns:
            Filtered query object
        """
        query = self.query()
        for field, value in filters.items():
            query = query.filter(getattr(self.model, field) == value)
        return query

    def get_by_filter(self, filters: dict) -> list[ModelType] | None:
        """
        Get multiple records by filter criteria.
        Example: get_by_filter({"user_id": 1, "code": "123456"})

        Args:
            filters: Dictionary of filter criteria.
        
        Returns: List of records or None if no records found.

        Raises:
            DatabaseError: If there is an error querying the database
        """
        try:
            return self._get_filtered_query(filters).all()
        except Exception as e:
            raise DatabaseError(detail=f"Error: {e}")

    def get_one_by_filter(self, filters: dict) -> ModelType | None:
        """
        Get one record by filter criteria.
        Example: get_one_by_filter({"user_id": 1, "code": "123456"})

        Args:
            filters: Dictionary of filter criteria.
        
        Returns: Single record or None if no record found.

        Raises:
            DatabaseError: If there is an error querying the database
        """
        try:
            return self._get_filtered_query(filters).first()
        except Exception as e:
            raise DatabaseError(detail=f"Error: {e}")

    def get_one(self, id: int) -> ModelType:
        """
        Get one record by id.
        Using filter() instead of get() for future RLS compatibility.

        Args:
            id: ID of the record to retrieve.

        Returns:
            Record with the given id.

        Raises:
            NotFoundError: If the record is not found
            DatabaseError: If there is an error querying the database
        """
        try:
            record = self.db.query(self.model).filter(self.model.id == id).first()

            if record is None:
                raise NotFoundError(
                    detail=f"Record with id {id} not found in {self.model.__name__}"
                )

            return record
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(detail=f"Error: {e}")

    def create(self, data: SchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            data: Pydantic model with create data

        Returns:
            Created model instance

        Raises:
            DatabaseError: If there is an error creating the record
        """
        try:
            record = self.model(**data.model_dump())
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(detail=f"Error creating record: {e}")

    def update(self, id: int, data: SchemaType) -> ModelType:
        """
        Update an existing record.
        Only updates fields that were set in the input data.

        Args:
            id: ID of the item to update
            data: Pydantic model with update data

        Returns:
            Updated model instance

        Raises:
            NotFoundError: If the record is not found
            BadRequestError: If no update data is provided
            DatabaseError: If there is an error updating the record
        """
        try:
            record = self.get_one(id)
            update_data = data.model_dump(
                exclude_unset=True
            )  # Only update fields that are provided

            if not update_data:
                raise BadRequestError(detail="No data to update")

            for field, value in update_data.items():
                setattr(record, field, value)

            self.db.commit()
            self.db.refresh(record)
            return record
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(detail=f"Error updating item: {e}")

    def update_by_filter(self, filters: dict, data: SchemaType) -> ModelType:
        """
        Update an record by filter criteria.
        Example: update_by_filter({"user_id": 1, "code": "123456"}, update_data)
        """
        try:
            # Get the record using filters
            query = self.query()
            for field, value in filters.items():
                query = query.filter(getattr(self.model, field) == value)

            record = query.first()
            if not record:
                raise NotFoundError(detail="Record not found with given filters")

            # Update the record with the provided data
            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                raise BadRequestError(detail="No data to update")

            for field, value in update_data.items():
                setattr(record, field, value)

            self.db.commit()
            self.db.refresh(record)
            return record
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(detail=f"Error updating record by filter: {e}")

    def update_multiple_by_filter(self, filters: dict, data: SchemaType) -> list[ModelType]:
        """
        Update multiple records that match the filter criteria.
        Example: update_multiple_by_filter({"status": "pending"}, update_data)

        Args:
            filters: Dictionary of filter criteria
            data: Pydantic model with update data

        Returns:
            List of updated model instances

        Raises:
            BadRequestError: If no update data is provided
            DatabaseError: If there is an error updating the records
        """
        try:
            # Get all matching records
            records = self._get_filtered_query(filters).all()
            
            # Prepare update data
            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                raise BadRequestError(detail="No data to update")

            # Update all records
            for record in records:
                for field, value in update_data.items():
                    setattr(record, field, value)

            self.db.commit()
            
            # Refresh all records to get updated values
            for record in records:
                self.db.refresh(record)
                
            return records
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(detail=f"Error updating records by filter: {e}")

    def delete(self, id: int) -> bool:
        """
        Delete an item by id.
        Returns True if successful, raises NotFoundError if item does not exist.
        """
        try:
            item = self.get_one(id)  # Will raise NotFoundError if not found
            self.db.delete(item)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(detail=f"Error deleting item: {e}")

    def delete_by_filter(self, filters: dict) -> bool:
        """
        Delete items matching multiple filter criteria.
        Example: delete_by_filter({"user_id": 1, "status": "active"})
        """
        try:
            query = self.query()
            for field, value in filters.items():
                query = query.filter(getattr(self.model, field) == value)

            items = query.all()
            for item in items:
                self.db.delete(item)

            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(detail=f"Error deleting items: {e}")
