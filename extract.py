import requests
import math
import json
import pandas as pd
import os
from datetime import datetime, timedelta, date
from typing import Dict, Union

# Fetch sensitive info from environment variables
PA_API_TOKEN = os.getenv("PA_API_TOKEN")
PA_USERNAME = os.getenv("PA_USERNAME")
PA_FILE_PATH = f"/home/{PA_USERNAME}/fetched_data.csv"

if not PA_API_TOKEN or not PA_USERNAME:
    raise ValueError("PA_API_TOKEN or PA_USERNAME environment variable is not set.")

def _do_post(data: Dict[str, str]) -> pd.DataFrame:
    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/TarihselVeriler.aspx",
    }

    response = requests.post(
        url="https://www.tefas.gov.tr//api/DB/BindHistoryInfo",
        headers=headers,
        data=data
    )

    response_str = response.content.decode("utf-8")
    response_json = json.loads(response_str)
    data = response_json.get("data", [])
    df = pd.DataFrame(data)
    df["TARIH"] = pd.to_datetime(df["TARIH"], unit="ms").dt.strftime("%Y-%m-%d")
    return df

def _parse_date(date: Union[str, datetime]) -> str:
    if isinstance(date, datetime):
        return datetime.strftime(date, "%d.%m.%Y")
    else:
        parsed = datetime.strptime(date, "%Y-%m-%d")
        return datetime.strftime(parsed, "%d.%m.%Y")

def fetch_info(start_date_initial, end_date_initial) -> pd.DataFrame:
    counter = 1
    start_date = start_date_initial
    end_date = end_date_initial
    range_date = end_date_initial - start_date_initial
    range_interval = 90
    info_result = pd.DataFrame()

    if range_date.days > range_interval:
        counter = math.ceil(range_date.days / range_interval)
        end_date = start_date + timedelta(days=range_interval)

    while counter > 0:
        counter -= 1
        data = {
            "fontip": "YAT",
            "bastarih": _parse_date(start_date),
            "bittarih": _parse_date(end_date),
        }

        info = _do_post(data)
        if not info.empty:
            info_result = pd.concat([info_result, info], ignore_index=True)

        if counter > 0:
            start_date = end_date + timedelta(days=1)
            end_date = start_date + timedelta(days=range_interval)
            if end_date > end_date_initial:
                end_date = end_date_initial

    return info_result

def upload_to_pythonanywhere(file_path: str):
    url = f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/files/path{PA_FILE_PATH}"
    headers = {"Authorization": f"Token {PA_API_TOKEN}"}

    with open(file_path, "rb") as file:
        response = requests.post(url, headers=headers, files={"content": file})

    if response.status_code == 200:
        print("File uploaded successfully!")
    else:
        print(f"Failed to upload file: {response.status_code}, {response.text}")

# Main Process
if __name__ == "__main__":
    date_start = date.today().strftime("%Y-%m-%d")
    date_end = date.today().strftime("%Y-%m-%d")

    start_date_initial = datetime.strptime(date_start, "%Y-%m-%d")
    end_date_initial = datetime.strptime(date_end, "%Y-%m-%d")

    fetched_data = fetch_info(start_date_initial, end_date_initial)
    csv_file = "fetched_data.csv"
    fetched_data.to_csv(csv_file, index=False)

    # Upload to PythonAnywhere
    upload_to_pythonanywhere(csv_file)
