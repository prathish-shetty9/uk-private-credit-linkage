"""
Step 1: filter the Companies House bulk file to active companies in the two sectors.

Input:  data/BasicCompanyData*.csv  (Free Company Data Product, downloaded manually)
Output: data/sector_companies.csv
"""
import glob
import pandas as pd

path = glob.glob("data/BasicCompanyData*.csv")[0]      # the bulk download specifically, not any CSV

SECTORS = {
    "87100": "care", "87300": "care",                  # residential nursing care; residential care for elderly/disabled
    "62012": "software", "58290": "software",          # software development; software publishing
}
WANTED = ["CompanyName", "CompanyNumber", "CompanyStatus", "IncorporationDate",
          "Accounts.AccountCategory", "Mortgages.NumMortCharges",
          "Mortgages.NumMortOutstanding", "SICCode.SicText_1"]

parts = []
# read the large file in pieces of 200,000 rows to limit memory use
for chunk in pd.read_csv(path, dtype=str, chunksize=200_000,       # dtype=str keeps leading zeros in company numbers
                         usecols=lambda c: c.strip() in WANTED):
    chunk.columns = chunk.columns.str.strip()                      # some column names have a leading space
    chunk["sic"] = chunk["SICCode.SicText_1"].str[:5]              # primary SIC code only, e.g. "87100"
    keep = chunk[chunk["sic"].isin(SECTORS) & (chunk["CompanyStatus"] == "Active")]
    parts.append(keep)

df = pd.concat(parts)
df["sector"] = df["sic"].map(SECTORS)
df["Mortgages.NumMortCharges"] = df["Mortgages.NumMortCharges"].astype(int)

print("Active companies per sector:")
print(df["sector"].value_counts())
print("\nAccount categories:")
print(df["Accounts.AccountCategory"].value_counts())

df.to_csv("data/sector_companies.csv", index=False)