#!/usr/bin/env python3
# KANDEX (Kannapolis Index)
# Copyright (C) 2026 Brad Spry
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""KANDEX (Kannapolis Index) — fetches quotes, stores a daily snapshot in
SQLite for trending, and prints a concise text summary for a Facebook post.

Usage:
    python kandex.py
"""

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import yfinance as yf

DB_PATH = Path(__file__).parent / "kandex.db"

COMPANIES = [
    ("GOOGL", "Alphabet"),
    ("AMZN", "Amazon"),
    ("CHWY", "Chewy"),
    ("GLW", "Corning"),
    ("LLY", "Eli Lilly"),
    ("SYY", "Sysco"),
    ("M", "Macy's"),
    ("WEST", "Westrock Coffee"),
    ("LOW", "Lowe's"),
    ("AEO", "American Eagle"),
]

BASELINE_INDEX = 1000.0
TREND_LOOKBACK_DAYS = 7


def init_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            PRIMARY KEY (date, symbol)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS kandex_index (
            date TEXT PRIMARY KEY,
            value REAL NOT NULL
        )
        """
    )
    conn.commit()


def fetch_quotes():
    """Returns {symbol: (last_price, previous_close)}."""
    quotes = {}
    for symbol, _ in COMPANIES:
        fi = yf.Ticker(symbol).fast_info
        quotes[symbol] = (fi.last_price, fi.previous_close)
    return quotes


def store_prices(conn, today, quotes):
    conn.executemany(
        "INSERT OR REPLACE INTO prices (date, symbol, price) VALUES (?, ?, ?)",
        [(today, symbol, price) for symbol, (price, _) in quotes.items()],
    )
    conn.commit()


def get_trend_price(conn, symbol, today):
    """Most recent stored price at least TREND_LOOKBACK_DAYS old, if any."""
    cutoff = (date.fromisoformat(today) - timedelta(days=TREND_LOOKBACK_DAYS)).isoformat()
    row = conn.execute(
        "SELECT price FROM prices WHERE symbol = ? AND date <= ? ORDER BY date DESC LIMIT 1",
        (symbol, cutoff),
    ).fetchone()
    return row[0] if row else None


def update_index(conn, today, avg_pct_change):
    """Compounds the composite index off the most recent prior day's value."""
    row = conn.execute(
        "SELECT value FROM kandex_index WHERE date < ? ORDER BY date DESC LIMIT 1",
        (today,),
    ).fetchone()
    prev_value = row[0] if row else BASELINE_INDEX
    new_value = prev_value * (1 + avg_pct_change / 100)
    conn.execute(
        "INSERT OR REPLACE INTO kandex_index (date, value) VALUES (?, ?)",
        (today, new_value),
    )
    conn.commit()
    return new_value, prev_value


def arrow(pct):
    if pct > 0.001:
        return "⬆️"
    if pct < -0.001:
        return "⬇️"
    return "➡️"


def build_report(conn, today, quotes):
    pct_changes = []
    stock_lines = []
    for symbol, name in COMPANIES:
        price, prev_close = quotes[symbol]
        pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0.0
        pct_changes.append(pct)

        trend_flag = ""
        trend_price = get_trend_price(conn, symbol, today)
        if trend_price:
            trend_pct = ((price - trend_price) / trend_price) * 100
            trend_flag = f"  (7d {arrow(trend_pct)}{trend_pct:+.1f}%)"

        stock_lines.append(
            f"{symbol} {name} — ${price:,.2f} {arrow(pct)} {pct:+.1f}%{trend_flag}"
        )

    avg_pct = sum(pct_changes) / len(pct_changes)
    index_value, prev_index = update_index(conn, today, avg_pct)
    index_pct = ((index_value - prev_index) / prev_index) * 100 if prev_index else 0.0

    title_mood = "🐂📈" if index_pct >= 0 else "🐻📉"
    lines = [f"Kannapolis Index (KANDEX) {title_mood}", datetime.now().strftime("%B %d, %Y"), ""]
    lines.extend(stock_lines)
    lines.append("")
    lines.append(f"KANDEX Composite: {index_value:,.2f}  {arrow(index_pct)} {index_pct:+.2f}%")
    return "\n".join(lines)


def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    today = date.today().isoformat()

    quotes = fetch_quotes()
    store_prices(conn, today, quotes)
    report = build_report(conn, today, quotes)

    print(report)
    conn.close()


if __name__ == "__main__":
    main()
