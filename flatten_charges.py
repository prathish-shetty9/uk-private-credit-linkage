"""
Step 4: flatten the raw charge files into one table, one row per lender per charge.

Input:  data/charges/*.json, data/sample.csv
Output: data/charges_flat.csv
"""
import json
import glob
import pandas as pd

sample = pd.read_csv("data/sample.csv", dtype=str)
sector_of = dict(zip(sample["CompanyNumber"], sample["sector"]))
expected = dict(zip(sample["CompanyNumber"], sample["Mortgages.NumMortCharges"].astype(int)))

rows, has_field, got = [], 0, {}
for path in sorted(glob.glob("data/charges/*.json")):        # sorted: same order on every machine
    with open(path) as f:
        company = json.load(f)
    number = company["company_number"]
    got[number] = len(company["items"])

    for charge in company["items"]:
        if "more_than_four_persons_entitled" in charge:
            has_field += 1
        lenders = charge.get("persons_entitled", [])
        base = {
            "company_number": number,
            "sector": sector_of.get(number),
            "charge_id": charge.get("links", {}).get("self"),
            "created_on": charge.get("created_on"),
            "status": charge.get("status"),
            "charge_type": charge.get("classification", {}).get("description"),
            "more_than_four": charge.get("more_than_four_persons_entitled", False),
        }
        if not lenders:                                      # no lender listed: keep the charge, mark it
            rows.append({**base, "lender_raw": None})
        for person in lenders:                               # several lenders on one charge -> several rows
            rows.append({**base, "lender_raw": person.get("name")})

df = pd.DataFrame(rows)
df.to_csv("data/charges_flat.csv", index=False)

print("Rows (lender x charge):", len(df))
print("Distinct charges:", df["charge_id"].nunique())
print("Charges with no lender listed:", df[df["lender_raw"].isna()]["charge_id"].nunique())
print("Charges containing the >4 lenders field at all:", has_field)
print("Charges flagged >4 lenders:", df[df["more_than_four"] == True]["charge_id"].nunique())
print("Distinct raw lender names:", df["lender_raw"].nunique())

# completeness: downloaded charges vs. the count in the bulk snapshot
diff = {k: got[k] - expected[k] for k in got if got[k] != expected.get(k)}
print("\nCompanies where downloaded count matches bulk file:", len(got) - len(diff), "of", len(got))
print("Largest differences (downloaded minus bulk):", sorted(diff.items(), key=lambda x: -abs(x[1]))[:5])