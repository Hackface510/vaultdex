# VaultDex - Collectibles Portfolio & Marketplace

A full-stack collectibles management app inspired by Holodex's UX model, built for serious collectors.

## What is VaultDex?

VaultDex is a **collectibles operating system** that lets users:

- 📦 Track collectibles in a personal portfolio
- 🌐 Keep items public or private
- 💰 List owned items for sale directly from their collection
- 🤝 Receive inquiries and offers on owned items
- 📊 View portfolio stats & gain/loss tracking
- 🔄 Automatic ownership transfer after purchase
- 🛒 Browse a peer-to-peer marketplace

Inspired by [Holodex](https://holodex.net)'s clean aggregation UX — but for physical collectibles (Pokémon, Magic, Comics, Sports Cards, etc.)

## Tech Stack

- **Backend**: Python FastAPI + SQLite
- **Frontend**: HTML/CSS/JS (Tailwind CSS)
- **Database**: SQLite (local file)

## Quick Start

### Requirements
- Python 3.10+

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Then open http://127.0.0.1:8000 in your browser.

### On Windows (no bash)
```
pip install fastapi uvicorn jinja2 pydantic
python app.py
```

## Features

### Portfolio Dashboard
- View all your collectibles in a grid
- Filter by category (Pokemon, Magic, Comics, etc.)
- See total portfolio value, cost basis, and gain/loss
- Toggle items between public and private visibility

### Asset Management
- Add new assets with title, category, type, condition, value, purchase price
- View detailed asset pages with gain/loss breakdown
- List items for sale directly from your collection

### Marketplace
- Browse all items listed for sale
- Buy items instantly (simulated purchase + ownership transfer)
- Make offers on items

### Ownership Transfer
- When a purchase is completed, the item automatically:
  - Moves from seller's inventory to buyer's inventory
  - Records the transfer in the ownership log

## Project Structure

```
vaultdex/
├── app.py          # FastAPI backend
├── index.html      # Frontend (HTML/CSS/JS)
├── requirements.txt
├── README.md
└── vaultdex.db     # SQLite database (auto-created)
```

## Roadmap

- [ ] Real authentication & multiple users
- [ ] Stripe payment integration
- [ ] Image upload from device
- [ ] Live auction mode (Whatnot-style)
- [ ] Mobile app (React Native)
- [ ] Price tracking & alerts

## Origins

Built from a ChatGPT conversation exploring a Holodex-inspired collectibles platform concept.
