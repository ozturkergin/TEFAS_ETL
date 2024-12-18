import requests, math, json
import pandas as pd

from datetime import datetime, timedelta, date
from typing import Dict, Union

def _do_post(data: Dict[str, str]) -> Dict[str, str]:
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
        data=data,
        proxies=None,
    )

    response_str = response.content.decode('utf-8')  # Decode the byte content to a string
    response_json = json.loads(response_str)  # Parse the JSON content
    data = response_json.get('data', [])  # Extract the `data` field
    df = pd.DataFrame(data)     # Convert the data to a pandas DataFrame
    df["TARIH"] = pd.to_datetime(df["TARIH"], unit='ms').dt.strftime("%Y-%m-%d")
    return df

def _parse_date(date: Union[str, datetime]) -> str:
    if isinstance(date, datetime):
        formatted = datetime.strftime(date, "%d.%m.%Y")
    elif isinstance(date, str):
        parsed = datetime.strptime(date, "%Y-%m-%d")
        formatted = datetime.strftime(parsed, "%d.%m.%Y")
    return formatted

def fetch_info(start_date_initial, end_date_initial):
    counter = 1
    start_date = start_date_initial
    end_date = end_date_initial
    range_date = end_date_initial - start_date_initial
    range_interval = 90
    info_result = pd.DataFrame()

    if range_date.days > range_interval:
        counter = range_date.days / range_interval
        counter = math.ceil(counter)
        end_date = start_date + timedelta(days=range_interval)

    while counter > 0:
        counter -= 1

        data = {
            "fontip": "YAT",
            "bastarih": _parse_date(start_date),
            "bittarih": _parse_date(end_date)
        }

        info = _do_post(data)
        info = pd.DataFrame(info)

        if not info.empty:
            info_result = pd.concat([info_result, info])
            info_result = info_result.reset_index(drop=True)
            info = info.reset_index(drop=True)

        if counter > 0:
            start_date = end_date + timedelta(days=1)
            end_date = end_date + timedelta(days=range_interval)
            if end_date > end_date_initial:
                end_date = end_date_initial

    return info_result

def fetch_info_serial(start_date_initial, end_date_initial):
    merged = pd.DataFrame()
    info = fetch_info(start_date_initial, end_date_initial)
    if not info.empty:
        merged = pd.concat([merged, info])
    return merged

# Calculate date range
date_start = date.today().strftime("%Y-%m-%d")
date_end = date.today().strftime("%Y-%m-%d")

start_date_initial = datetime.strptime(date_start, "%Y-%m-%d")
end_date_initial = datetime.strptime(date_end or date_start, "%Y-%m-%d")

fetched_data = pd.DataFrame()
fetched_data = fetch_info_serial(start_date_initial, end_date_initial)
fetched_data.to_csv("fetched_data.csv", index=False)
