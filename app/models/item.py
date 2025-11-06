from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ItemType(str, Enum):
    MOVIE = "movie"
    PRODUCT = "product"
    BOOK = "book"


class MovieMetadata(BaseModel):
    director: Optional[str] = None
    cast: Optional[List[str]] = Field(default_factory=list)
    release_date: Optional[str] = None
    poster_url: Optional[str] = None
    duration_minutes: Optional[int] = None


class ProductMetadata(BaseModel):
    brand: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    stock: Optional[int] = None
    specifications: Optional[dict] = Field(default_factory=dict)


class BookMetadata(BaseModel):
    author: Optional[str] = None
    isbn: Optional[str] = None
    publication_date: Optional[str] = None
    cover_url: Optional[str] = None
    pages: Optional[int] = None
    publisher: Optional[str] = None


class ItemBase(BaseModel):
    description: str
    genres: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class MovieCreate(ItemBase):
    title: str
    metadata: Optional[MovieMetadata] = None


class ProductCreate(ItemBase):
    name: str
    category: str
    metadata: Optional[ProductMetadata] = None


class BookCreate(ItemBase):
    title: str
    metadata: Optional[BookMetadata] = None


class ItemUpdate(BaseModel):
    description: Optional[str] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class Item(BaseModel):
    id: str
    item_type: ItemType
    title: Optional[str] = None
    name: Optional[str] = None
    description: str
    genres: List[str]
    tags: List[str]
    metadata: dict
    created_at: datetime
    updated_at: datetime


class ItemInDB(Item):
    pass
