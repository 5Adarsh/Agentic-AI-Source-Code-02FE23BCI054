"""
Pagination helper schemas and utilities.
"""
import math
from typing import Generic, List, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


def paginate(query: Query, page: int = 1, page_size: int = 20) -> Page:
    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
