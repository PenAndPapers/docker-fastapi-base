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
        Return a query object for the given model.
        Raise a NotFoundError if the items are not found.
        """
        try:
            return self.db.query(self.model)
        except Exception as e:
            raise DatabaseError(detail=f"Error querying items: {e}")

    def get_one(self, id: int) -> ModelType | None:
        """
        Get one item by id.
        Using filter() instead of get() for future RLS compatibility.
        Raise a NotFoundError if the item is not found.
        """
        item = self.db.query(self.model).filter(self.model.id == id).first()

        if item is None:
            raise NotFoundError(
                detail=f"Item with id {id} not found in {self.model.__name__}"
            )

        return item

    def create(self, data: SchemaType) -> ModelType:
        """
        Create a new item.

        Args:
            data: Pydantic model with create data

        Returns:
            Created model instance
        """
        try:
            item = self.model(**data.model_dump())
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(detail=f"Error creating item: {e}")

    def update(self, id: int, data: SchemaType) -> ModelType:
        """
        Update an existing item.
        Only updates fields that were set in the input data.
        """
        try:
            item = self.get_one(id)
            update_data = data.model_dump(
                exclude_unset=True
            )  # Only update fields that are provided

            if not update_data:
                raise BadRequestError(detail="No data to update")

            for field, value in update_data.items():
                setattr(item, field, value)

            self.db.commit()
            self.db.refresh(item)
            return item
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(detail=f"Error updating item: {e}")

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
