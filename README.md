# gc-scraper

Tracks US Green Card processing times for PERM and I-485 visa bulletins. Data is automatically scraped weekly and displayed on a simple dashboard.

## Live Dashboard

View the latest data at: https://pxmyh.github.io/gc-scraper/

## What It Tracks

- **PERM**: Processing date from [DOL FLAG](https://flag.dol.gov/processingtimes) (Analyst Review queue)
- **I-485**: EB3 China Mainland priority dates from [State Dept Visa Bulletins](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html), with historical trend visualization

## Project Structure

```
gc-scraper/
├── data/                    # Output data files
│   ├── perm_time.txt        # Current PERM processing date
│   ├── visa_bulletin_dates.csv  # Historical I-485 data
│   ├── visa_bulletin_plot.png   # I-485 trend chart
│   └── last_updated.txt     # Last update timestamp
├── src/gc_scraper/
│   └── i485_parser.py       # I-485 visa bulletin scraper
├── index.html               # Dashboard webpage
└── .github/workflows/
    └── update-data.yml      # Automated weekly scraper
```

## How It Works

A GitHub Actions workflow runs every Wednesday at 9am EST:

1. **PERM**: Downloads DOL page, extracts processing date using `pup`
2. **I-485**: Runs Python scraper to fetch visa bulletin data, generates CSV and plot
3. **Commits** any changes to the repo

The dashboard (`index.html`) is served via GitHub Pages and fetches the latest data files.

## Run Locally

**Prerequisites**: Python 3.10+, [uv](https://github.com/astral-sh/uv)

```bash
# Install dependencies
uv sync

# Run I-485 scraper
uv run python src/gc_scraper/i485_parser.py
```

For PERM scraping, install [pup](https://github.com/ericchiang/pup) and run:
```bash
curl -o data/perm.html https://flag.dol.gov/processingtimes
pup 'td.xl71 text{}' < data/perm.html | head -1 > data/perm_time.txt
```

## Data Caching

The I-485 scraper caches downloaded HTML pages in `visa_bulletin_pages/` and skips already-parsed months in the CSV. This makes subsequent runs fast (~10 seconds vs 2-3 minutes).

## License

MIT
