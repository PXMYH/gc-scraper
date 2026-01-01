import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# Function to load existing CSV data
def load_existing_data(csv_filename):
    """Load existing CSV data into a dictionary keyed by calendar date"""
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


# Function to check cache or download HTML
def get_cached_or_download(url, filepath):
    """Check if HTML file exists, otherwise download and save"""
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


# Function to convert date from "01OCT13" to "YYMM" format
def convert_date(date_str):
    date_obj = datetime.strptime(date_str, "%d%b%y")
    # Add "20" as a prefix to the last two digits of the year
    full_year = "20" + date_obj.strftime("%y")
    return full_year + "-" + date_obj.strftime("%m")


# Function to calculate the time difference in months between two dates
def calculate_time_difference_months(calendar_date_str, pd_date_str):
    calendar_date = datetime.strptime(calendar_date_str, "%Y-%m")
    pd_date = datetime.strptime(pd_date_str, "%Y-%m")

    # Calculate the difference in months
    months_difference = (calendar_date.year - pd_date.year
                         ) * 12 + calendar_date.month - pd_date.month

    return months_difference


# Generate a plot from the data and save it as an image
def generate_plot(data):
    # Extract calendar dates and time differences from the data
    calendar_dates = [item[0] for item in data]
    time_differences = [item[2] for item in data]

    # Create a Matplotlib figure
    plt.figure(figsize=(10, 6))
    plt.plot(calendar_dates, time_differences, marker='o', linestyle='-')

    # Customize the plot
    plt.title("Time Gap vs Calendar Date")
    plt.xlabel("Calendar Date")
    plt.ylabel("Time Gap (months)")

    # Format the x-axis labels to display every nth label (adjust n as needed)
    n = 3  # Display every 3rd label
    plt.xticks(range(0, len(calendar_dates), n),
               calendar_dates[::n],
               rotation=45)

    plt.grid(True)

    # Save the plot as an image
    plt.savefig("visa_bulletin_plot.png", bbox_inches='tight')
    plt.close()  # Close the figure to free up resources


# Create a directory to store the downloaded pages
if not os.path.exists('visa_bulletin_pages'):
    os.makedirs('visa_bulletin_pages')

# Define the base URL
base_url = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/"

# Define the years to loop through
start_year = 2016
current_year = datetime.now().year

# Define the months
months = [
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december"
]

# Create a CSV file to store the extracted dates
csv_filename = "visa_bulletin_dates.csv"

# Load existing parsed data to avoid re-processing
existing_data = load_existing_data(csv_filename)
print(f"Loaded {len(existing_data)} existing records from CSV")

# Initialize a list to store the newly parsed data
data = []

# Loop through the years and months
for year in range(start_year, current_year + 1):
    for month_index, month in enumerate(months):
        # Adjust the year if the month is November or later
        dos_fiscal_year = year + 1 if month_index >= 9 else year
        calendar_year = year

        # Check if this date was already parsed
        year_month = f"{calendar_year}-{month_index + 1:02}"
        if year_month in existing_data:
            print(f"Skipping {year_month} - already parsed")
            continue

        # Form the URL for the specific visa bulletin page
        url = base_url + f"{dos_fiscal_year}/visa-bulletin-for-{month}-{calendar_year}.html"

        # Check cache or download HTML
        filepath = f"visa_bulletin_pages/{month}_{calendar_year}.html"
        html_content = get_cached_or_download(url, filepath)

        # Check if we got HTML content
        if html_content:
            # Parse the HTML content of the page
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract the date using the specified CSS selector
            date_selector = "body > div.tsg-rwd-body-frame-row > div.contentbody > div.tsg-rwd-main-copy-frame > div.tsg-rwd-main-copy-body-frame.withrail > div.tsg-rwd-content-page-parsysxxx.parsys > div:nth-child(5) > div > p > table > tbody > tr:nth-child(4) > td:nth-child(3)"
            date_element = soup.select_one(date_selector)

            date_str = date_element.text.strip(
            ) if date_element else 'Date not found'

            # Convert the date to "YYMM" format using the function
            formatted_date = convert_date(date_str)
            print(f"EB3 For China Mainland born PD date is {formatted_date}")

            # Calculate the time difference in months
            time_difference = calculate_time_difference_months(
                year_month, formatted_date)
            print(f"Time Difference (months): {time_difference}")

            # Append the data to the list
            data.append((year_month, formatted_date, time_difference))
        else:
            print(f"Failed to download: {month} {calendar_year}")

# Merge existing data with newly parsed data
print(f"Newly parsed records: {len(data)}")
all_data = list(existing_data.values()) + data
all_data.sort(key=lambda x: x[0])  # Sort by calendar date
print(f"Total records: {len(all_data)}")

# Write the merged data to CSV file
with open(csv_filename, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write the header row with column names
    csv_writer.writerow(
        ["Calendar Date", "PD Date", "Time Difference (months)"])

    # Write the data rows
    csv_writer.writerows(all_data)

print(f"Data written to {csv_filename}")

# Generate the plot and save it as an image
generate_plot(all_data)
print("Plot generated and saved as visa_bulletin_plot.png")
