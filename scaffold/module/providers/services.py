from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..repository import {Module}Repository
from ..service import {Module}Service, {Module}Policy
from ..controller import {Module}Controller


def get_{module}_repository(db: Session = Depends(get_db)) -> {Module}Repository:
    return {Module}Repository(db)


def get_{module}_service(
    repository: {Module}Repository = Depends(get_{module}_repository),
    policy: {Module}Policy = Depends(),
) -> {Module}Service:
    return {Module}Service(repository, policy)


def get_{module}_controller(
    service: {Module}Service = Depends(get_{module}_service),
) -> {Module}Controller:
    return {Module}Controller(service)
