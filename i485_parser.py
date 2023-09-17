import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime


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

# Create a CSV file to store the extracted dates
csv_filename = "visa_bulletin_dates.csv"

# Initialize a list to store the data
data = []

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

            # Extract the date using the specified CSS selector
            date_selector = "body > div.tsg-rwd-body-frame-row > div.contentbody > div.tsg-rwd-main-copy-frame > div.tsg-rwd-main-copy-body-frame.withrail > div.tsg-rwd-content-page-parsysxxx.parsys > div:nth-child(5) > div > p > table > tbody > tr:nth-child(4) > td:nth-child(3)"
            date_element = soup.select_one(date_selector)

            date_str = date_element.text.strip(
            ) if date_element else 'Date not found'

            # Convert the date to "YYMM" format using the function
            formatted_date = convert_date(date_str)
            print(f"EB3 For China Mainland born PD date is {formatted_date}")

            # Interpolate the "Year-Month" column name
            year_month = f"{calendar_year}-{month_index + 1:02}"  # Format as "year-month"

            # Calculate the time difference in months
            time_difference = calculate_time_difference_months(
                year_month, formatted_date)
            print(f"Time Difference (months): {time_difference}")

            # Append the data to the list
            data.append((year_month, formatted_date, time_difference))
        else:
            print(f"Failed to download: {month} {calendar_year}")

# Write the extracted dates and time difference to a CSV file
with open(csv_filename, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    # Write the header row with column names
    csv_writer.writerow(
        ["Calendar Date", "PD Date", "Time Difference (months)"])

    # Write the data rows
    csv_writer.writerows(data)

print(f"Data written to {csv_filename}")
