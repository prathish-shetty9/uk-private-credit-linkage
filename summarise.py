"""
Step 8: summary statistics.

Non-bank lender = debt_fund, specialist_nonbank or property_investor.
Not counted as non-bank lenders: sponsor (PE/VC investors), government, individual,
agent_trustee (lenders hidden), other, unresolved. These are reported separately.
Shares include outstanding and satisfied charges.

Input:  data/charges_clean.csv, data/lender_map.csv
Output: printed; save with  python summarise.py > results.txt
"""
import pandas as pd

charges = pd.read_csv("data/charges_clean.csv", dtype=str)
lmap = pd.read_csv("data/lender_map.csv", dtype=str).fillna("")

df = charges.merge(lmap[["lender_clean", "parent", "type"]], on="lender_clean", how="left")
df["type"] = df["type"].fillna("no_lender_listed")                     # the one charge with no lender
df["year"] = pd.to_numeric(df["created_on"].str[:4], errors="coerce")

NONBANK = ["debt_fund", "specialist_nonbank", "property_investor"]

# 1. what kinds of parties hold the charges (share of lender records)
print("1. Lender records by type (%):")
print((df["type"].value_counts(normalize=True) * 100).round(1))

# 2. share of companies with at least one non-bank lender / debt fund / sponsor / agent / individual
co = df.groupby(["sector", "company_number"]).agg(
    nonbank=("type", lambda t: t.isin(NONBANK).any()),
    debt_fund=("type", lambda t: (t == "debt_fund").any()),
    sponsor=("type", lambda t: (t == "sponsor").any()),
    agent=("type", lambda t: (t == "agent_trustee").any()),
    individual=("type", lambda t: (t == "individual").any()),
).reset_index()
print("\n2. Share of companies with at least one... (%), by sector:")
print((co.groupby("sector")[["nonbank", "debt_fund", "sponsor", "agent", "individual"]].mean() * 100).round(1))
print("Companies per sector:")
print(co["sector"].value_counts())

# 3. concentration: top 5 lender groups among identified lenders (banks and non-banks)
ident = df[df["type"].isin(["bank"] + NONBANK)]
by_parent = ident.groupby("parent")["charge_id"].nunique().sort_values(ascending=False)
print("\n3. Top 5 lender groups by number of charges:")
print(by_parent.head(5))
print("Top 5 share of identified lender-charge links: %.1f%%" % (by_parent.head(5).sum() / by_parent.sum() * 100))

# 4. trend: share of charges with a non-bank lender, by period and sector
ch = df.groupby("charge_id").agg(year=("year", "first"), sector=("sector", "first"),
                                 nonbank=("type", lambda t: t.isin(NONBANK).any())).reset_index()
ch["period"] = pd.cut(ch["year"], bins=[0, 2012, 2019, 2100], labels=["pre-2013", "2013-2019", "2020+"])
print("\n4. Share of charges with a non-bank lender (%), by period and sector:")
print((ch.pivot_table(index="period", columns="sector", values="nonbank", aggfunc="mean", observed=False) * 100).round(1))
print("\nCharges per period and sector:")
print(ch.pivot_table(index="period", columns="sector", values="charge_id", aggfunc="count", observed=False))

# 5. data quality
print("\n5. Data quality:")
print("Unresolved records: %.1f%%" % ((df["type"] == "unresolved").mean() * 100))
print("Agent/trustee records (lenders hidden): %.1f%%" % ((df["type"] == "agent_trustee").mean() * 100))
print("Individual lender records: %.1f%%" % ((df["type"] == "individual").mean() * 100))

# 6. bounds check: how far could unresolved names move the headline?
def share(nonbank_types):
    c = df.groupby(["sector", "company_number"])["type"].apply(lambda t: t.isin(nonbank_types).any())
    return (c.groupby("sector").mean() * 100).round(1)

print("\n6. Companies with a non-bank lender (%):")
print("   if unresolved = all banks:     ", share(NONBANK).to_dict())
print("   if unresolved = all non-banks: ", share(NONBANK + ["unresolved"]).to_dict())