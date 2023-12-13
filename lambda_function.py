import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
import boto3
from io import StringIO
import os

# Function to convert text to float or np.nan
def convert_to_float(value):
    return float(value.strip()) if value.strip() else np.nan

# Function to parse and convert date string
def parse_and_convert_date(date_str):
    date_str += ", {0}".format(datetime.now().year)
    parsed_date = datetime.strptime(date_str, '%d %b, %H:%M, %Y')
    return parsed_date.strftime('%Y-%m-%d %H:%M:%S')

# Function to generate S3 key
def generate_s3_key():
    date = datetime.now()
    return "{0}/{1}/{2}/{3}.csv".format(date.year, date.month, date.day, date.strftime('%H-%M-%S'))

def lambda_handler(event,context):
    # Set the URL
    url = "https://rate.am/en/"
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="rb")
    rows = table.find_all("tr")[2:]

    # Get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Initialize lists to store data
    bank_names, dates, usd_buy, usd_sell, eur_buy, eur_sell, rub_buy, rub_sell, gbp_buy, gbp_sell = ([] for _ in range(10))

    # Iterate through rows and extract data
    for row in rows:
        columns = row.find_all("td")

        # Check if there are enough columns to extract data
        if len(columns) >= 13:
            bank_name_elem = columns[1].find("a")

            if bank_name_elem:
                bank_name = bank_name_elem.text
                date_str = parse_and_convert_date(columns[4].text)
                usd_sell_rate = convert_to_float(columns[5].text)
                usd_buy_rate = convert_to_float(columns[6].text)
                eur_sell_rate = convert_to_float(columns[7].text)
                eur_buy_rate = convert_to_float(columns[8].text)
                rub_sell_rate = convert_to_float(columns[9].text)
                rub_buy_rate = convert_to_float(columns[10].text)
                gbp_sell_rate = convert_to_float(columns[11].text)
                gbp_buy_rate = convert_to_float(columns[12].text)

                # Append data to lists
                bank_names.append(bank_name)
                dates.append(date_str)
                usd_buy.append(usd_buy_rate)
                usd_sell.append(usd_sell_rate)
                eur_buy.append(eur_buy_rate)
                eur_sell.append(eur_sell_rate)
                rub_buy.append(rub_buy_rate)
                rub_sell.append(rub_sell_rate)
                gbp_buy.append(gbp_buy_rate)
                gbp_sell.append(gbp_sell_rate)

    # Create a DataFrame
    data = {
        "bank": bank_names,
        "date": dates,
        "usd_buy": usd_buy,
        "usd_sell": usd_sell,
        "eur_buy": eur_buy,
        "eur_sell": eur_sell,
        "rub_buy": rub_buy,
        "rub_sell": rub_sell,
        "gbp_buy": gbp_buy,
        "gbp_sell": gbp_sell
    }

    df = pd.DataFrame(data)
    
    # Upload DataFrame to S3
    bucket_name = os.environ.get('RATES_BUCKET')
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_resource = boto3.resource('s3')
    object_key = generate_s3_key()
    s3_resource.Object(bucket_name, object_key).put(Body=csv_buffer.getvalue())
