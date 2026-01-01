import os
import csv
from datetime import datetime

import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

# Configuration constants
BASE_URL = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/"
START_YEAR = 2016
CSV_FILENAME = "data/visa_bulletin_dates.csv"
CACHE_DIR = "visa_bulletin_pages"
PLOT_FILENAME = "data/visa_bulletin_plot.png"
MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]


def load_existing_data(csv_filename):
    """Load existing CSV data into a dictionary keyed by calendar date."""
    existing_data = {}
    if os.path.exists(csv_filename):
        with open(csv_filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data[row['Calendar Date']] = (
                    row['Calendar Date'],
                    row['PD Date'],
                    int(row['Time Difference (months)'])
                )
    return existing_data


def get_cached_or_download(url, filepath):
    """Check if HTML file exists, otherwise download and save."""
    if os.path.exists(filepath):
        print(f"Using cached file: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"Downloading: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return response.text
        return None


def convert_date(date_str):
    """Convert date from '01OCT13' to 'YYYY-MM' format."""
    try:
        date_obj = datetime.strptime(date_str, "%d%b%y")
        return f"20{date_obj.strftime('%y')}-{date_obj.strftime('%m')}"
    except ValueError:
        print(f"Warning: Could not parse date '{date_str}'")
        return None


def calculate_time_difference_months(calendar_date_str, pd_date_str):
    """Calculate the time difference in months between two dates."""
    calendar_date = datetime.strptime(calendar_date_str, "%Y-%m")
    pd_date = datetime.strptime(pd_date_str, "%Y-%m")
    return (calendar_date.year - pd_date.year) * 12 + calendar_date.month - pd_date.month


def generate_plot(data, output_filename):
    """Generate a plot from the data and save it as an image."""
    calendar_dates = [item[0] for item in data]
    time_differences = [item[2] for item in data]

    plt.figure(figsize=(10, 6))
    plt.plot(calendar_dates, time_differences, marker='o', linestyle='-')
    plt.title("Time Gap vs Calendar Date")
    plt.xlabel("Calendar Date")
    plt.ylabel("Time Gap (months)")

    # Display every 3rd label on x-axis
    n = 3
    plt.xticks(range(0, len(calendar_dates), n), calendar_dates[::n], rotation=45)
    plt.grid(True)
    plt.savefig(output_filename, bbox_inches='tight')
    plt.close()


def main():
    """Main entry point for the I-485 visa bulletin scraper."""
    # Create cache directory
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    current_year = datetime.now().year

    # Load existing parsed data to avoid re-processing
    existing_data = load_existing_data(CSV_FILENAME)
    print(f"Loaded {len(existing_data)} existing records from CSV")

    # Initialize list for newly parsed data
    data = []

    # Loop through years and months
    for year in range(START_YEAR, current_year + 1):
        for month_index, month in enumerate(MONTHS):
            # DOS fiscal year adjustment (Oct-Dec are next fiscal year)
            dos_fiscal_year = year + 1 if month_index >= 9 else year
            calendar_year = year
            year_month = f"{calendar_year}-{month_index + 1:02}"

            # Skip if already parsed
            if year_month in existing_data:
                print(f"Skipping {year_month} - already parsed")
                continue

            # Build URL and filepath
            url = f"{BASE_URL}{dos_fiscal_year}/visa-bulletin-for-{month}-{calendar_year}.html"
            filepath = f"{CACHE_DIR}/{month}_{calendar_year}.html"

            # Get HTML content
            html_content = get_cached_or_download(url, filepath)
            if not html_content:
                print(f"Failed to download: {month} {calendar_year}")
                continue

            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")
            date_selector = (
                "body > div.tsg-rwd-body-frame-row > div.contentbody > "
                "div.tsg-rwd-main-copy-frame > div.tsg-rwd-main-copy-body-frame.withrail > "
                "div.tsg-rwd-content-page-parsysxxx.parsys > div:nth-child(5) > "
                "div > p > table > tbody > tr:nth-child(4) > td:nth-child(3)"
            )
            date_element = soup.select_one(date_selector)

            if not date_element:
                print(f"Warning: Could not find date element for {year_month}")
                continue

            date_str = date_element.text.strip()
            formatted_date = convert_date(date_str)

            if not formatted_date:
                print(f"Warning: Skipping {year_month} due to date parsing error")
                continue

            print(f"EB3 China Mainland PD date: {formatted_date}")

            time_difference = calculate_time_difference_months(year_month, formatted_date)
            print(f"Time Difference (months): {time_difference}")

            data.append((year_month, formatted_date, time_difference))

    # Merge existing data with newly parsed data
    print(f"Newly parsed records: {len(data)}")
    all_data = list(existing_data.values()) + data
    all_data.sort(key=lambda x: x[0])
    print(f"Total records: {len(all_data)}")

    # Write merged data to CSV
    with open(CSV_FILENAME, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Calendar Date", "PD Date", "Time Difference (months)"])
        csv_writer.writerows(all_data)
    print(f"Data written to {CSV_FILENAME}")

    # Generate plot
    generate_plot(all_data, PLOT_FILENAME)
    print(f"Plot generated and saved as {PLOT_FILENAME}")


if __name__ == "__main__":
    main()
