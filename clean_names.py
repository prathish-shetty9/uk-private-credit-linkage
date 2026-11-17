"""
Step 5: standardise lender names so variants of the same entity match.

Lowercases, removes bracketed text, cuts off "as security agent/trustee ..." phrases,
strips punctuation, a leading "the", "governor and company of the", and legal suffixes.
The hand labels in label_lenders.py match these cleaned names exactly, so this step is
frozen: changing it would silently break those matches.

Input:  data/charges_flat.csv
Output: data/charges_clean.csv  (adds lender_clean and a descriptive lender_role column)
"""
import re
import pandas as pd

df = pd.read_csv("data/charges_flat.csv", dtype=str)

ROLE_WORDS = ["security agent", "security trustee", "as agent", "as trustee", "trustee"]

SUFFIXES = [r"\bplc\b", r"\bp l c\b", r"\blimited\b", r"\bltd\b", r"\bllp\b", r"\binc\b",
            r"\bs a r l\b", r"\bsarl\b", r"\bgmbh\b", r"\bag\b", r"\blp\b", r"\bn a\b"]

def clean(name):
    if pd.isna(name):
        return None
    s = name.lower()                                            # everything lowercase
    s = re.sub(r"\(.*?\)", " ", s)                              # drop anything in brackets
    s = re.split(r"\b(as|in its capacity as) (security |collateral |administrative )?(agent|trustee)\b", s)[0]   # cut "as agent/trustee for ..." off the end
    s = s.replace("&", " and ")                                 # & -> and
    s = re.sub(r"[^a-z0-9 ]", " ", s)                           # punctuation -> spaces
    s = re.sub(r"\s+", " ", s).strip()                          # collapse spaces early (the fix)
    s = re.sub(r"^the\s+", "", s)                               # leading "the"
    s = s.replace("governor and company of the ", "")           # old formal bank names
    for suf in SUFFIXES:
        s = re.sub(suf, " ", s)                                 # legal suffixes
    s = re.sub(r"\s+", " ", s).strip()                          # tidy spaces again at the end
    return s

def role(name):
    if pd.isna(name):
        return None
    low = name.lower()
    for w in ROLE_WORDS:
        if w in low:
            return w
    return None

df["lender_clean"] = df["lender_raw"].apply(clean)
df["lender_role"] = df["lender_raw"].apply(role)

df.to_csv("data/charges_clean.csv", index=False)

print("Distinct raw names:  ", len(df["lender_raw"].dropna().unique()))
print("Distinct clean names:", df["lender_clean"].nunique())
print("Rows with an agent/trustee role:", df["lender_role"].notna().sum())
print("\nTop 40 clean names:")
print(df["lender_clean"].value_counts().head(40))