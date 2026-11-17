"""
Step 2: keep mid-market companies with at least one registered charge, then draw the sample.

Mid-market proxy: last accounts filed as FULL, GROUP or MEDIUM (i.e. above the small-company
thresholds). Audit-exempt subsidiaries are excluded to avoid counting a group's debt twice.

Input:  data/sector_companies.csv
Output: data/sample.csv  (150 companies per sector, fixed random seed)
"""
import os
import pandas as pd

df = pd.read_csv("data/sector_companies.csv", dtype=str)
df["Mortgages.NumMortCharges"] = df["Mortgages.NumMortCharges"].astype(int)

MID_MARKET = ["FULL", "GROUP", "MEDIUM"]
PER_SECTOR = 150
SEED = 42                                                        # fixed seed: same sample every run

mid = df[df["Accounts.AccountCategory"].isin(MID_MARKET)]
with_charges = mid[mid["Mortgages.NumMortCharges"] >= 1]

print("Mid-market companies per sector:")
print(mid["sector"].value_counts())
print("\n...of which have at least one charge:")
print(with_charges["sector"].value_counts())

# draw each sector separately with the same seed
sample = pd.concat([g.sample(n=min(PER_SECTOR, len(g)), random_state=SEED)
                    for _, g in with_charges.groupby("sector")])

print("\nFinal sample:")
print(sample["sector"].value_counts())

# guard: never silently replace an existing sample with a different one
out = "data/sample.csv"
if os.path.exists(out):
    old = set(pd.read_csv(out, dtype=str)["CompanyNumber"])
    if old != set(sample["CompanyNumber"]):
        raise SystemExit("New draw differs from existing data/sample.csv. Not overwriting.")
    print("\nSample identical to existing file.")
sample.to_csv(out, index=False)