import os

import requests
from bs4 import BeautifulSoup

# Create a directory to store the downloaded pages
if not os.path.exists('visa_bulletin_pages'):
    os.makedirs('visa_bulletin_pages')

# Define the base URL
base_url = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/"

# Define the years to loop through
start_year = 2016
current_year = 2023  # You can adjust this as needed

# Define the months
months = [
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december"
]

# Loop through the years and months
for year in range(start_year, current_year + 1):
    for month_index, month in enumerate(months):
        # Adjust the year if the month is November or later
        dos_fiscal_year = year + 1 if month_index >= 9 else year
        calendar_year = year

        # Form the URL for the specific visa bulletin page
        url = base_url + f"{dos_fiscal_year}/visa-bulletin-for-{month}-{calendar_year}.html"
        print(f"The Download URL {url}")

        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, "html.parser")

            # Save the page content to a file
            filename = f"visa_bulletin_pages/{month}_{calendar_year}.html"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(str(soup))
            print(f"Downloaded: {month} {calendar_year}")
        else:
            print(f"Failed to download: {month} {calendar_year}")
