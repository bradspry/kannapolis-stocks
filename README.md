# Kannapolis Index (KANDEX)

*by Brad Spry, Kannapolitan*

A tiny stock tracker that snapshots Kannapolis-area companies, stores daily
history in a local SQLite database (for trending), and prints a concise
report.

```
Kannapolis Index (KANDEX) 🐻📉
July 19, 2026

GOOGL Alphabet — $346.77 ⬇️ -3.0%
AMZN Amazon — $247.23 ⬇️ -1.5%
CHWY Chewy — $20.93 ⬇️ -2.1%
GLW Corning — $154.61 ⬇️ -0.7%
LLY Eli Lilly — $1,179.11 ⬆️ +0.6%
SYY Sysco — $81.69 ⬇️ -1.0%
M Macy's — $23.68 ⬇️ -1.7%
WEST Westrock Coffee — $7.68 ⬇️ -0.3%
LOW Lowe's — $208.73 ⬇️ -3.0%
AEO American Eagle — $17.03 ⬇️ -2.3%

KANDEX Composite: 985.07  ⬇️ -1.49%
```

## Companies tracked

| Symbol | Company |
| --- | --- |
| GOOGL | Alphabet (Google) |
| AMZN | Amazon |
| CHWY | Chewy |
| GLW | Corning |
| LLY | Eli Lilly |
| SYY | Sysco |
| M | Macy's |
| WEST | Westrock Coffee |
| LOW | Lowe's Companies |
| AEO | American Eagle Outfitters |

## Setup

```
pip3 install --user -r requirements.txt
```

## Usage

```
python3 kandex.py
```

Run it once a day, after market close, for the cleanest results — see
[How it works](#how-it-works) for why.

## How it works

- Quotes are pulled live via [`yfinance`](https://github.com/ranaroussi/yfinance).
- Each run stores a dated price snapshot per symbol in `kandex.db` (SQLite,
  created automatically, ignored by git). This history powers the 7-day
  trend annotations that appear once a week of data has accumulated.
- Per-stock daily % change is computed against Yahoo's previous close, so
  it's accurate even on the very first run.
- **KANDEX Composite** is an equal-weighted index seeded at 1,000.0. Each
  day it compounds the average % change across all ten stocks onto the
  prior day's value — similar in spirit to how real market indices track
  cumulative return rather than a raw price average. Re-running the script
  multiple times in the same day is safe; the composite always compounds
  off the last *prior* day's value, not the last run.
- The title emoji flips between 🐂📈 (bull) and 🐻📉 (bear) based on
  whether the composite moved up or down that day.

## Disclaimer

Data is sourced from Yahoo Finance via the unofficial `yfinance` library.
This project is for informational and entertainment purposes only and is
not financial advice.

## License

[GPL-3.0](LICENSE)
