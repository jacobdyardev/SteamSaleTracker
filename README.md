# Steam Sale Tracker

Python-based Steam sale tracking tool that retrieves live sale listings, extracts pricing and discount information, normalizes results, and exports structured CSV reports.

## Features

- Live Steam sale retrieval
- Infinite-scroll pagination support
- HTML parsing from JSON responses
- Automatic price extraction with fallback handling
- Discount tracking
- Structured CSV export
- Error handling and validation
- Configurable result limits

## Workflow

```text
Build Request Parameters
        ↓
Fetch Steam Search Results
        ↓
Parse HTML Response Data
        ↓
Extract Pricing Information
        ↓
Normalize Game Records
        ↓
Generate Structured Rows
        ↓
Export CSV Report
```

## Example Configuration

```python
STEAM_SEARCH_URL = "https://store.steampowered.com/search/results/"

OUTPUT_FILE = "steam_sale_games.csv"

PAGE_SIZE = 100
MAX_GAMES = 100
```

## Example Output

```text
Wallpaper Engine
Original: $4.99
Sale: $3.99
Discount: -20%
https://store.steampowered.com/app/431960

Cyberpunk 2077
Original: $59.99
Sale: $29.99
Discount: -50%
https://store.steampowered.com/app/1091500

The Witcher 3: Wild Hunt
Original: $39.99
Sale: $7.99
Discount: -80%
https://store.steampowered.com/app/292030

Saved 100 games to steam_sale_games.csv
```

## Technical Highlights

- Uses Steam search endpoints directly
- Handles dynamic infinite-scroll pagination
- Supports price extraction fallback logic
- Normalizes extracted data into structured rows
- Separates request, parsing, formatting, and export responsibilities

## Status

Functional implementation / active development
