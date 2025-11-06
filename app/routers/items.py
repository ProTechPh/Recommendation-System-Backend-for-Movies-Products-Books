from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.dependencies import get_db
from app.models.item import (
    ItemType, MovieCreate, ProductCreate, BookCreate,
    Item, ItemUpdate
)


router = APIRouter(prefix="/items", tags=["items"])


async def create_item(
    db: AsyncIOMotorDatabase,
    item_type: ItemType,
    item_data: dict,
    metadata: dict
) -> Item:
    """Helper function to create an item"""
    item_dict = {
        "item_type": item_type.value,
        "description": item_data.get("description", ""),
        "genres": item_data.get("genres", []),
        "tags": item_data.get("tags", []),
        "metadata": metadata or {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    if item_type == ItemType.MOVIE:
        item_dict["title"] = item_data.get("title")
    elif item_type == ItemType.PRODUCT:
        item_dict["name"] = item_data.get("name")
        item_dict["category"] = item_data.get("category")
    elif item_type == ItemType.BOOK:
        item_dict["title"] = item_data.get("title")
    
    result = await db.items.insert_one(item_dict)
    item_dict["id"] = str(result.inserted_id)
    return Item(**item_dict)


@router.post("/movies", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie: MovieCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new movie"""
    metadata = movie.metadata.dict() if movie.metadata else {}
    item_data = {
        "title": movie.title,
        "description": movie.description,
        "genres": movie.genres,
        "tags": movie.tags
    }
    return await create_item(db, ItemType.MOVIE, item_data, metadata)


@router.post("/products", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new product"""
    metadata = product.metadata.dict() if product.metadata else {}
    item_data = {
        "name": product.name,
        "category": product.category,
        "description": product.description,
        "genres": product.genres,
        "tags": product.tags
    }
    return await create_item(db, ItemType.PRODUCT, item_data, metadata)


@router.post("/books", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new book"""
    metadata = book.metadata.dict() if book.metadata else {}
    item_data = {
        "title": book.title,
        "description": book.description,
        "genres": book.genres,
        "tags": book.tags
    }
    return await create_item(db, ItemType.BOOK, item_data, metadata)


@router.get("/movies", response_model=List[Item])
async def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    genre: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all movies with optional filtering"""
    query = {"item_type": ItemType.MOVIE.value}
    if genre:
        query["genres"] = genre
    
    cursor = db.items.find(query).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    
    return [Item(**{**item, "id": str(item["_id"])}) for item in items]


@router.get("/products", response_model=List[Item])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all products with optional filtering"""
    query = {"item_type": ItemType.PRODUCT.value}
    if category:
        query["category"] = category
    if genre:
        query["genres"] = genre
    
    cursor = db.items.find(query).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    
    return [Item(**{**item, "id": str(item["_id"])}) for item in items]


@router.get("/books", response_model=List[Item])
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    genre: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all books with optional filtering"""
    query = {"item_type": ItemType.BOOK.value}
    if genre:
        query["genres"] = genre
    
    cursor = db.items.find(query).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    
    return [Item(**{**item, "id": str(item["_id"])}) for item in items]


@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific item by ID"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID"
        )
    
    item = await db.items.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    item["id"] = str(item["_id"])
    return Item(**item)


@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: str,
    item_update: ItemUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update an item"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID"
        )
    
    item = await db.items.find_one({"_id": ObjectId(item_id)})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    update_data = {}
    if item_update.description is not None:
        update_data["description"] = item_update.description
    if item_update.genres is not None:
        update_data["genres"] = item_update.genres
    if item_update.tags is not None:
        update_data["tags"] = item_update.tags
    if item_update.metadata is not None:
        existing_metadata = item.get("metadata", {})
        existing_metadata.update(item_update.metadata)
        update_data["metadata"] = existing_metadata
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.items.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_data}
        )
    
    updated_item = await db.items.find_one({"_id": ObjectId(item_id)})
    updated_item["id"] = str(updated_item["_id"])
    return Item(**updated_item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete an item"""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID"
        )
    
    result = await db.items.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return None
