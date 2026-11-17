"""
Step 6: one row per cleaned lender name, with how often it appears.

Used to decide where hand-labelling effort goes: the most frequent names cover most records.
Parent and type are assigned in the next step (label_lenders.py).

Input:  data/charges_clean.csv
Output: data/lender_list.csv
"""
import pandas as pd

df = pd.read_csv("data/charges_clean.csv", dtype=str)

lenders = (df.groupby("lender_clean")
             .agg(rows=("charge_id", "size"),                         # lender x charge records
                  companies=("company_number", "nunique"),            # distinct borrowers
                  sectors=("sector", lambda s: ", ".join(sorted(s.dropna().unique()))),
                  example_raw=("lender_raw", "first"))                # one original spelling, for checking
             .reset_index()
             .sort_values(["rows", "lender_clean"], ascending=[False, True])   # ties broken by name
             .reset_index(drop=True))

lenders["cum_share"] = (lenders["rows"].cumsum() / lenders["rows"].sum()).round(3)

lenders.to_csv("data/lender_list.csv", index=False)

print("Clean lender names:", len(lenders))
print("Names needed to reach 85% of records:", (lenders["cum_share"] < 0.85).sum() + 1)