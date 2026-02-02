r"""
Lesson 13 MCP Server: CSV Query Tools

This MCP server exposes tools for querying the concerts-async.csv file.
Instead of passing all CSV data to the LLM, the LLM calls these tools
to retrieve only the specific data it needs, saving input tokens.

Run directly: python lesson13_mcp_server.py (for testing)
Used by: lesson13_mcp_has_task.py via MCPServerStdio
"""

import csv
from pathlib import Path
from collections import Counter
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP('CSV Query Server')

CSV_FILE = Path("concerts-async.csv")


def _load_rows() -> list[dict]:
    """Load CSV rows as list of dicts"""
    if not CSV_FILE.exists():
        return []
    with open(CSV_FILE, 'r', newline='') as f:
        return list(csv.DictReader(f))


@mcp.tool()
def get_total_records() -> str:
    """Get the total number of records in the CSV database"""
    rows = _load_rows()
    return f"Total records: {len(rows)}"


@mcp.tool()
def list_all_bands() -> str:
    """List all unique band names in the database"""
    rows = _load_rows()
    bands = sorted(set(row.get('band_name', '') for row in rows if row.get('band_name')))
    return f"Bands ({len(bands)}): {', '.join(bands)}"


@mcp.tool()
def list_all_genres() -> str:
    """List all unique genres in the database with counts"""
    rows = _load_rows()
    genres = Counter(row.get('genre', 'Unknown') for row in rows if row.get('genre'))
    result = [f"{genre}: {count}" for genre, count in genres.most_common()]
    return f"Genres:\n" + "\n".join(result)


@mcp.tool()
def list_all_countries() -> str:
    """List all unique countries in the database with counts"""
    rows = _load_rows()
    countries = Counter(row.get('country', 'Unknown') for row in rows if row.get('country'))
    result = [f"{country}: {count}" for country, count in countries.most_common()]
    return f"Countries:\n" + "\n".join(result)


@mcp.tool()
def get_bands_by_genre(genre: str) -> str:
    """Get all bands of a specific genre (case-insensitive partial match)"""
    rows = _load_rows()
    genre_lower = genre.lower()
    matches = [row for row in rows if genre_lower in row.get('genre', '').lower()]
    if not matches:
        return f"No bands found with genre matching '{genre}'"
    bands = sorted(set(row.get('band_name', '') for row in matches))
    return f"Bands with genre '{genre}' ({len(bands)}): {', '.join(bands)}"


@mcp.tool()
def get_bands_by_country(country: str) -> str:
    """Get all bands from a specific country (case-insensitive partial match)"""
    rows = _load_rows()
    country_lower = country.lower()
    matches = [row for row in rows if country_lower in row.get('country', '').lower()]
    if not matches:
        return f"No bands found from country matching '{country}'"
    bands = sorted(set(row.get('band_name', '') for row in matches))
    return f"Bands from '{country}' ({len(bands)}): {', '.join(bands)}"


@mcp.tool()
def get_band_details(band_name: str) -> str:
    """Get all details for a specific band (case-insensitive partial match)"""
    rows = _load_rows()
    band_lower = band_name.lower()
    matches = [row for row in rows if band_lower in row.get('band_name', '').lower()]
    if not matches:
        return f"No band found matching '{band_name}'"
    results = []
    for row in matches:
        results.append(
            f"- {row.get('band_name')}: {row.get('genre')} from {row.get('country')}, "
            f"playing at {row.get('venue')}, {row.get('location')} on {row.get('date')}"
        )
    return "\n".join(results)


@mcp.tool()
def count_bands_by_genre(genre: str) -> str:
    """Count how many bands match a specific genre"""
    rows = _load_rows()
    genre_lower = genre.lower()
    matches = [row for row in rows if genre_lower in row.get('genre', '').lower()]
    unique_bands = set(row.get('band_name', '') for row in matches)
    return f"Number of {genre} bands: {len(unique_bands)}"


@mcp.tool()
def search_records(search_term: str) -> str:
    """Search all fields for a term (case-insensitive). Returns matching records."""
    rows = _load_rows()
    term_lower = search_term.lower()
    matches = []
    for row in rows:
        for value in row.values():
            if term_lower in str(value).lower():
                matches.append(row)
                break
    if not matches:
        return f"No records found containing '{search_term}'"
    results = [f"Found {len(matches)} record(s) containing '{search_term}':"]
    for row in matches[:10]:  # Limit to 10 results
        results.append(f"- {row.get('band_name')}: {row.get('genre')} ({row.get('country')})")
    if len(matches) > 10:
        results.append(f"... and {len(matches) - 10} more")
    return "\n".join(results)


if __name__ == '__main__':
    mcp.run()
