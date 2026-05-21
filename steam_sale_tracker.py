import csv
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# Store the Steam search endpoint in one clear place.
STEAM_SEARCH_URL = "https://store.steampowered.com/search/results/"
OUTPUT_FILE = "steam_sale_games.csv"
PAGE_SIZE = 100
MAX_GAMES = 100


# Build the query params Steam expects for sale results.
def build_params(start: int = 0, count: int = PAGE_SIZE) -> dict[str, str]:
    return {
        "query": "",
        "start": str(start),
        "count": str(count),
        "dynamic_data": "",
        "sort_by": "_ASC",
        "specials": "1",
        "filter": "topsellers",
        "category1": "998",
        "infinite": "1",
    }


# Request sale data from Steam and return the JSON response.
def fetch_sale_results(params: dict[str, str]) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(
        STEAM_SEARCH_URL,
        params=params,
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


# Clean up text so prices and titles are easy to save and print.
def clean_text(text: str) -> str:
    return " ".join(text.split())


# Pull price values from the standard tags, with a fallback for odd layouts.
def extract_prices(game) -> tuple[str, str, str]:
    discount_tag = game.select_one("div.discount_pct")
    original_price_tag = game.select_one("div.discount_original_price")
    sale_price_tag = game.select_one("div.discount_final_price")

    discount_percent = clean_text(discount_tag.get_text()) if discount_tag else ""
    original_price = (
        clean_text(original_price_tag.get_text()) if original_price_tag else ""
    )
    sale_price = clean_text(sale_price_tag.get_text()) if sale_price_tag else ""

    if original_price and sale_price:
        return original_price, sale_price, discount_percent

    price_values = [
        clean_text(text)
        for text in game.select_one("div.discount_prices").stripped_strings
    ] if game.select_one("div.discount_prices") else []

    if len(price_values) >= 2:
        original_price = original_price or price_values[0]
        sale_price = sale_price or price_values[-1]
    elif len(price_values) == 1:
        sale_price = sale_price or price_values[0]

    return original_price, sale_price, discount_percent


# Parse the result HTML inside the JSON response.
def parse_sale_games(response_data: dict) -> list[dict[str, str]]:
    results_html = response_data.get("results_html", "")
    if not results_html:
        return []

    soup = BeautifulSoup(results_html, "html.parser")
    rows: list[dict[str, str]] = []

    for game in soup.select("a.search_result_row"):
        title_tag = game.select_one("span.title")

        title = clean_text(title_tag.get_text()) if title_tag else ""
        original_price, sale_price, discount_percent = extract_prices(game)

        relative_url = game.get("href", "").strip()
        game_url = urljoin("https://store.steampowered.com", relative_url)

        if not title:
            continue

        if not original_price or not sale_price:
            continue

        rows.append(
            {
                "Title": title,
                "Original Price": original_price,
                "Sale Price": sale_price,
                "Discount %": discount_percent,
                "URL": game_url,
            }
        )

    return rows


# Load more results the same way Steam does with infinite scroll.
def collect_sale_games(max_games: int = MAX_GAMES) -> list[dict[str, str]]:
    sale_games: list[dict[str, str]] = []
    start = 0

    while len(sale_games) < max_games:
        params = build_params(start=start, count=PAGE_SIZE)
        response_data = fetch_sale_results(params)
        page_games = parse_sale_games(response_data)

        if not page_games:
            break

        sale_games.extend(page_games)
        start += PAGE_SIZE

    return sale_games[:max_games]


# Save the sale results to a CSV file with clean headers.
def save_to_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    fieldnames = ["Title", "Original Price", "Sale Price", "Discount %", "URL"]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# Run the full Steam sale tracker flow.
def main() -> None:
    output_path = Path(OUTPUT_FILE)

    try:
        sale_games = collect_sale_games()
    except requests.RequestException as error:
        print(f"Request failed: {error}")
        return
    except ValueError as error:
        print(f"Could not read Steam response as JSON: {error}")
        return

    if not sale_games:
        print("No sale games were found.")
        return

    for game in sale_games:
        print(
            f"{game['Title']} | "
            f"Original: {game['Original Price']} | "
            f"Sale: {game['Sale Price']} | "
            f"Discount: {game['Discount %']} | "
            f"{game['URL']}"
        )

    save_to_csv(sale_games, output_path)
    print(f"\nSaved {len(sale_games)} sale games to {output_path.name}")


if __name__ == "__main__":
    main()
