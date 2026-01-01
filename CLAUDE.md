# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project tracks US Green Card processing times through automated web scraping:
- **I-485** (Adjustment of Status): Tracks EB3 China Mainland priority dates from visa bulletins
- **PERM** (Labor Certification): Monitors current processing times

Both scrapers run automatically via GitHub Actions and commit results to the repository for historical tracking and visualization.

## Development Commands

```bash
# Install dependencies
uv sync

# Run I-485 scraper manually
uv run python src/gc_scraper/i485_parser.py

# Lint code
uv run ruff check .

# Type check
uv run pyright
```

## Architecture

### I-485 Scraper
**File**: [src/gc_scraper/i485_parser.py](src/gc_scraper/i485_parser.py)

Scrapes historical visa bulletins from travel.state.gov (2016-present) and extracts EB3 China Mainland priority dates:

1. **Scraping**: Loops through years/months, constructs URLs, downloads HTML pages
2. **Parsing**: Uses BeautifulSoup with CSS selector: `tbody > tr:nth-child(4) > td:nth-child(3)`
3. **Processing**: Converts dates ("01OCT13" → "2013-10"), calculates time gaps between calendar dates and priority dates
4. **Output**: Generates `visa_bulletin_dates.csv` and `visa_bulletin_plot.png`

**Key functions**:
- `convert_date()`: Converts date format for processing
- `calculate_time_difference_months()`: Computes month gap between calendar date and priority date
- `generate_plot()`: Creates matplotlib visualization of time trends

### PERM Scraper
**File**: [.github/workflows/perm-scraper.yml](.github/workflows/perm-scraper.yml)

Bash-based scraper using curl and pup (HTML parser):

1. Downloads HTML from flag.dol.gov/processingtimes
2. Extracts processing time using pup with CSS selector
3. Saves to `perm_time.txt`

Simpler than I-485 scraper since it only extracts a single current data point.

### Automation

Two GitHub Actions workflows auto-commit scraped data:

- **I-485**: [.github/workflows/i485-scraper.yml](.github/workflows/i485-scraper.yml)
  - Schedule: Weekly (Wednesdays 7:27 AM UTC)
  - Runs on Ubuntu with Python 3.10
  - Uses UV for dependency management

- **PERM**: [.github/workflows/perm-scraper.yml](.github/workflows/perm-scraper.yml)
  - Schedule: Daily (1:00 PM UTC / 9 AM EST)
  - Runs on macOS (requires Homebrew for pup)
  - Bash-based with curl/pup

Both workflows auto-commit results with timestamp messages.

### Dashboard
**File**: [index.html](index.html)

Simple HTML page that displays:
- I-485 trend plot (embedded PNG)
- Current PERM processing time (fetched via JavaScript from `perm_time.txt`)

## Key Technical Details

**Python Environment**:
- Strict Python 3.10 requirement (`>=3.10,<3.11` in pyproject.toml)
- UV package manager for all operations (not pip)
- Dependencies: requests, beautifulsoup4, matplotlib

**CSS Selector Fragility**:
- I-485 parser uses specific CSS selector pointing to table cell position
- If travel.state.gov restructures their HTML, selector will break
- PERM scraper similarly depends on specific table structure

**Date Handling**:
- Input format: "01OCT13" (day, 3-letter month, 2-digit year)
- Output format: "YYYY-MM" (e.g., "2013-10")
- Time gaps calculated in months between calendar date and priority date

**No Test Suite**:
- Project validates through production scraping
- Monitor GitHub Actions for scraper failures

## Important Considerations

When modifying scrapers:

1. **CSS Selectors**: Test thoroughly - these are brittle and site-specific
2. **Date Parsing**: The `convert_date()` function assumes 20xx years (will break after 2099)
3. **External Dependencies**: Scrapers depend on government site availability and structure
4. **Historical Data**: `visa_bulletin_pages/` directory contains 203+ archived HTML files
5. **Generated Files**: `visa_bulletin_dates.csv`, `visa_bulletin_plot.png`, `perm_time.txt` are auto-generated
6. **GitHub Actions**: Both workflows require repository write access to auto-commit results
