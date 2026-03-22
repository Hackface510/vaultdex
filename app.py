from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title="VaultDex API")

DB_PATH = "vaultdex.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        display_name TEXT,
        bio TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        asset_type TEXT NOT NULL,
        condition TEXT,
        current_value REAL DEFAULT 0,
        purchase_price REAL DEFAULT 0,
        qty INTEGER DEFAULT 1,
        visibility TEXT DEFAULT 'private',
        for_sale INTEGER DEFAULT 0,
        accepting_offers INTEGER DEFAULT 0,
        featured INTEGER DEFAULT 0,
        image TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        seller_id INTEGER NOT NULL,
        price REAL NOT NULL,
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (asset_id) REFERENCES assets(id),
        FOREIGN KEY (seller_id) REFERENCES users(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_id INTEGER NOT NULL,
        buyer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        message TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (listing_id) REFERENCES listings(id),
        FOREIGN KEY (buyer_id) REFERENCES users(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS ownership_transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        from_user_id INTEGER NOT NULL,
        to_user_id INTEGER NOT NULL,
        transfer_price REAL,
        transfer_date TEXT DEFAULT (datetime('now')),
        notes TEXT
    )""")
    
    # Seed default user if not exists
    c.execute("SELECT id FROM users WHERE username = 'collector1'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, display_name, bio) VALUES (?, ?, ?)",
                  ("collector1", "Dre Walker", "Serious collector. Pokémon, Magic, Comics."))
        user_id = c.lastrowid
        
        seed_assets = [
            (user_id, "Scarlet & Violet 151 Elite Trainer Box", "Pokemon", "Sealed Product", "Mint", 129, 84, 1, "public", 0, 1, 1, "https://images.unsplash.com/photo-1607537573965-12f856af48e9?w=400", "Sealed ETB"),
            (user_id, "Black Lotus Alpha", "Magic", "Card", "HP", 8500, 6200, 1, "public", 1, 0, 0, "https://images.unsplash.com/photo-1606761568499-6d2451b23c66?w=400", "Classic alpha lotus"),
            (user_id, "MTG Savannah Lions", "Magic", "Card", "Mint", 45, 30, 2, "public", 0, 0, 0, "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400", "Placeholder for MTG layout demo"),
            (user_id, "Amazing Spider-Man #300", "Comics", "Graded Comic", "CGC 8.5", 540, 420, 1, "public", 0, 1, 0, "https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?w=400", "First Venom appearance"),
            (user_id, "Charizard VMAX Rainbow Rare", "Pokemon", "Card", "PSA 10", 380, 220, 1, "public", 1, 1, 1, "https://images.unsplash.com/photo-1613771404784-3a5686aa2be3?w=400", "Rainbow rare - graded gem mint"),
            (user_id, "One Piece Monkey D. Luffy OP01-120 SEC", "One Piece TCG", "Card", "NM", 280, 180, 1, "private", 0, 0, 0, "https://images.unsplash.com/photo-1601513445506-2ab0d4fb4229?w=400", "Super rare secret rare"),
        ]
        
        for a in seed_assets:
            c.execute("""INSERT INTO assets (user_id, title, category, asset_type, condition, current_value, 
                         purchase_price, qty, visibility, for_sale, accepting_offers, featured, image, notes) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", a)
    
    conn.commit()
    conn.close()

init_db()

# Serve the frontend
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r") as f:
        return f.read()

# ---- API Routes ----

@app.get("/api/stats")
async def get_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total, SUM(current_value) as total_value, SUM(purchase_price) as total_cost FROM assets WHERE user_id = 1")
    row = c.fetchone()
    conn.close()
    total = row['total'] or 0
    total_value = row['total_value'] or 0
    total_cost = row['total_cost'] or 0
    return {
        "total_items": total,
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_gain": round(total_value - total_cost, 2),
        "gain_pct": round(((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0, 1)
    }

@app.get("/api/assets")
async def get_assets():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM assets WHERE user_id = 1 ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

class AssetCreate(BaseModel):
    title: str
    category: str
    asset_type: str
    condition: Optional[str] = "NM"
    current_value: Optional[float] = 0
    purchase_price: Optional[float] = 0
    qty: Optional[int] = 1
    visibility: Optional[str] = "private"
    notes: Optional[str] = ""
    image: Optional[str] = ""

@app.post("/api/assets")
async def create_asset(asset: AssetCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("""INSERT INTO assets (user_id, title, category, asset_type, condition, current_value,
                 purchase_price, qty, visibility, notes, image) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
              (1, asset.title, asset.category, asset.asset_type, asset.condition, 
               asset.current_value, asset.purchase_price, asset.qty, asset.visibility,
               asset.notes, asset.image))
    asset_id = c.lastrowid
    conn.commit()
    c.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
    row = c.fetchone()
    conn.close()
    return dict(row)

@app.patch("/api/assets/{asset_id}/visibility")
async def toggle_visibility(asset_id: int, request: Request):
    body = await request.json()
    visibility = body.get("visibility", "private")
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE assets SET visibility = ? WHERE id = ? AND user_id = 1", (visibility, asset_id))
    conn.commit()
    conn.close()
    return {"id": asset_id, "visibility": visibility}

@app.post("/api/assets/{asset_id}/list")
async def list_asset(asset_id: int, request: Request):
    body = await request.json()
    price = body.get("price", 0)
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE assets SET for_sale = 1, accepting_offers = 1 WHERE id = ? AND user_id = 1", (asset_id,))
    c.execute("INSERT INTO listings (asset_id, seller_id, price) VALUES (?,?,?)", (asset_id, 1, price))
    conn.commit()
    conn.close()
    return {"success": True, "asset_id": asset_id, "price": price}

@app.delete("/api/assets/{asset_id}/unlist")
async def unlist_asset(asset_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE assets SET for_sale = 0, accepting_offers = 0 WHERE id = ?", (asset_id,))
    c.execute("UPDATE listings SET status = 'cancelled' WHERE asset_id = ? AND status = 'active'", (asset_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/marketplace")
async def get_marketplace():
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT a.*, l.price as listing_price, l.id as listing_id, u.display_name as seller_name
                 FROM assets a 
                 JOIN listings l ON l.asset_id = a.id AND l.status = 'active'
                 JOIN users u ON u.id = a.user_id
                 WHERE a.for_sale = 1""")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

class OfferCreate(BaseModel):
    listing_id: int
    amount: float
    message: Optional[str] = ""

@app.post("/api/offers")
async def create_offer(offer: OfferCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO offers (listing_id, buyer_id, amount, message) VALUES (?,?,?,?)",
              (offer.listing_id, 1, offer.amount, offer.message))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Offer submitted!"}

@app.post("/api/listings/{listing_id}/buy")
async def buy_now(listing_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT l.*, a.title, a.user_id as seller_id FROM listings l JOIN assets a ON a.id = l.asset_id WHERE l.id = ? AND l.status = 'active'", (listing_id,))
    listing = c.fetchone()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing = dict(listing)
    
    # Complete the purchase
    c.execute("UPDATE listings SET status = 'sold' WHERE id = ?", (listing_id,))
    c.execute("UPDATE assets SET for_sale = 0, accepting_offers = 0, user_id = 1 WHERE id = ?", (listing['asset_id'],))
    c.execute("""INSERT INTO ownership_transfers (asset_id, from_user_id, to_user_id, transfer_price)
                 VALUES (?,?,?,?)""", (listing['asset_id'], listing['seller_id'], 1, listing['price']))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"You purchased {listing['title']} for ${listing['price']}!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
