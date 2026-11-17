"""
Step 3: download every registered charge for each sampled company from the Companies House API.

Requires the environment variable CH_API_KEY (free REST key from Companies House).
Input:  data/sample.csv
Output: data/charges/<company_number>.json  (one file per company; existing files are skipped)
"""
import os
import json
import time
from datetime import date
import requests
import pandas as pd

API_KEY = os.environ["CH_API_KEY"]                      # never hard-code the key
BASE = "https://api.company-information.service.gov.uk"
OUT = "data/charges"
os.makedirs(OUT, exist_ok=True)

sample = pd.read_csv("data/sample.csv", dtype=str)
n = len(sample)

for i, number in enumerate(sample["CompanyNumber"], start=1):
    out_file = f"{OUT}/{number}.json"
    if os.path.exists(out_file):                        # already downloaded: skip, so reruns resume
        continue

    items, start, total, ok = [], 0, 0, True
    while True:                                         # the API returns at most 100 charges per page
        r = requests.get(f"{BASE}/company/{number}/charges",
                         params={"items_per_page": 100, "start_index": start},
                         auth=(API_KEY, ""))            # Basic auth: key as username, empty password
        time.sleep(0.6)                                 # stay under 600 requests per 5 minutes
        if r.status_code != 200:
            print(number, "failed with", r.status_code)
            ok = False
            break
        data = r.json()
        page = data.get("items", [])
        items += page
        total = data.get("total_count", 0)
        if len(items) >= total or not page:             # all charges fetched, or nothing more returned
            break
        start += 100

    if not ok:                                          # don't save a failed download as if complete
        continue

    with open(out_file, "w") as f:
        json.dump({"company_number": number, "total_count": total,
                   "retrieved_on": date.today().isoformat(), "items": items}, f)

    print(f"{i}/{n}  {number}  {len(items)} of {total} charges")