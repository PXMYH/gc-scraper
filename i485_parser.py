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
current_year = 2016  # You can adjust this as needed

# Define the months
months = [
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december"
]
# months = ["january"]

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
        soup = BeautifulSoup(response.text, "html.parser")

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, "html.parser")

            # Save the page content to a file
            filename = f"visa_bulletin_pages/{month}_{calendar_year}.html"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(str(soup.prettify()))
            print(f"Downloaded: {month} {calendar_year}")

            # Extract the date using the specified CSS selector
            # The EB catagory table is the first of three tables after selection
            # and the date is the 3rd in the table
            # verified this all the way back to 2016 and it has been the case
            date_selector = "body > div.tsg-rwd-body-frame-row > div.contentbody > div.tsg-rwd-main-copy-frame > div.tsg-rwd-main-copy-body-frame.withrail > div.tsg-rwd-content-page-parsysxxx.parsys > div:nth-child(5) > div > p > table > tbody > tr:nth-child(4) > td:nth-child(3)"
            date_element = soup.css.select_one(date_selector)

            date = date_element.text.strip(
            ) if date_element else 'Date not found'
            print(f"EB3 For China Mainland born PD date is {date}")
        else:
            print(f"Failed to download: {month} {calendar_year}")
