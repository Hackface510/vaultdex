"""
FastAPI routes for TCGDex API integration endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from tcgdex_api import TCGDexAPI

router = APIRouter(prefix="/api/tcgdex", tags=["tcgdex"])
api = TCGDexAPI()

# Cards routes
@router.get("/cards")
async def list_cards(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    """Fetch all cards with pagination"""
    cards = await api.get_cards({"skip": skip, "limit": limit})
    if cards is None:
        raise HTTPException(status_code=500, detail="Failed to fetch cards from TCGDex API")
    return {"data": cards}

@router.get("/cards/{card_id}")
async def get_card_detail(card_id: str):
    """Fetch a single card by ID"""
    card = await api.get_card(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found")
    return card

# Sets routes
@router.get("/sets")
async def list_sets(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    """Fetch all card sets"""
    sets = await api.get_sets({"skip": skip, "limit": limit})
    if sets is None:
        raise HTTPException(status_code=500, detail="Failed to fetch sets from TCGDex API")
    return {"data": sets}

@router.get("/sets/{set_id}")
async def get_set_detail(set_id: str):
    """Fetch a single set by ID"""
    card_set = await api.get_set(set_id)
    if card_set is None:
        raise HTTPException(status_code=404, detail=f"Set {set_id} not found")
    return card_set

@router.get("/sets/{set_id}/{local_id}")
async def get_card_by_set(set_id: str, local_id: str):
    """Fetch a card by set ID and local ID"""
    card = await api.get_card_by_set_and_local_id(set_id, local_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card not found in set {set_id} with local ID {local_id}")
    return card

# Series routes
@router.get("/series")
async def list_series():
    """Fetch all series"""
    series = await api.get_series()
    if series is None:
        raise HTTPException(status_code=500, detail="Failed to fetch series from TCGDex API")
    return {"data": series}

@router.get("/series/{series_id}")
async def get_series_detail(series_id: str):
    """Fetch a single series by ID"""
    series = await api.get_series_by_id(series_id)
    if series is None:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")
    return series

# Types route
@router.get("/types")
async def list_types():
    """Fetch all card types"""
    types = await api.get_types()
    if types is None:
        raise HTTPException(status_code=500, detail="Failed to fetch types from TCGDex API")
    return {"data": types}

# Rarities route
@router.get("/rarities")
async def list_rarities():
    """Fetch all rarities"""
    rarities = await api.get_rarities()
    if rarities is None:
        raise HTTPException(status_code=500, detail="Failed to fetch rarities from TCGDex API")
    return {"data": rarities}

# Illustrators route
@router.get("/illustrators")
async def list_illustrators(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500)):
    """Fetch all illustrators"""
    illustrators = await api.get_illustrators({"skip": skip, "limit": limit})
    if illustrators is None:
        raise HTTPException(status_code=500, detail="Failed to fetch illustrators from TCGDex API")
    return {"data": illustrators}

# Categories route
@router.get("/categories")
async def list_categories():
    """Fetch all categories"""
    categories = await api.get_categories()
    if categories is None:
        raise HTTPException(status_code=500, detail="Failed to fetch categories from TCGDex API")
    return {"data": categories}