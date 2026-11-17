# uk-private-credit-linkage

A borrower-to-lender dataset for UK mid-market companies in two sectors, residential care and software, built from registered charges at Companies House. The aim is to show who lends to these companies, and in particular how much of that lending comes from debt funds rather than banks.

## Why this project

Private credit is now a major source of debt finance for mid-sized European companies, and most of it comes from funds rather than banks. The data needed to study it is spread across fund reports, company registers and filings. This project tests how far one public source, the UK charges register, can go towards linking individual borrowers to their lenders.

The two sectors are chosen to contrast. Residential care (SIC 87100 and 87300) is asset-heavy, heavily sponsor-owned and has a long history of property-backed financing. Software (SIC 62012 and 58290) is asset-light, so lenders secure on the business rather than on property, and it draws specialist lenders such as venture debt providers and direct lending funds.

## Why the UK and not Germany

The UK is the only major European jurisdiction where the link between borrower and secured lender is public. When a UK company grants security over its assets, the charge is registered at Companies House and names the persons entitled, usually the lender or a security agent.

Germany has no equivalent. Sicherungsübereignung (security transfer of movable assets) and Globalzession (blanket assignment of receivables) are not registered anywhere, and Grundschulden (land charges) sit in the Grundbuch, which is not publicly searchable. The German gap is part of the findings, not a failure of the project.

## Pipeline

First download the Companies House [Free Company Data Product](https://download.companieshouse.gov.uk/en_output.html) and place the `BasicCompanyData*.csv` file in `data/`. Then run the scripts in this order:

```bash
python build_sample.py
python make_sample.py
python pull_charges.py        # needs CH_API_KEY; about 6 minutes for 300 companies
python flatten_charges.py
python clean_names.py
python make_lender_list.py
python label_lenders.py
python summarise.py > results.txt
```

| Step | Script | What it does |
|---|---|---|
| 1 | `build_sample.py` | Filters the bulk file to active companies whose primary SIC code is in the two sectors (12,066 care, 112,488 software) and keeps account category and charge counts |
| 2 | `make_sample.py` | Keeps mid-market companies (last accounts FULL, GROUP or MEDIUM; audit-exempt subsidiaries excluded to avoid double-counting group debt) with at least one registered charge (760 care, 895 software), then draws 150 per sector with a fixed seed (42). Refuses to overwrite an existing sample with a different draw |
| 3 | `pull_charges.py` | Downloads every registered charge for each sample company from the Companies House API, paging 100 at a time and staying under the rate limit. Saves one JSON file per company with a retrieval date in `data/charges/`, skips files already downloaded so reruns resume, and never saves a failed download |
| 4 | `flatten_charges.py` | Turns the charge files into one row per lender per charge (keeping creation date, status and charge type), keeps charges with no lender listed, and checks the downloaded charge counts against the Companies House bulk file |
| 5 | `clean_names.py` | Standardises lender names so variants of one entity match: lowercases, drops bracketed text, cuts off "as security agent/trustee for ..." phrases, strips punctuation, old formal bank names and legal suffixes. Records any agent or trustee role in a separate `lender_role` column. Frozen, because the hand labels match these cleaned names exactly |
| 6 | `make_lender_list.py` | Builds one row per clean name with its record count, number of distinct borrowers, sectors, an example raw spelling and cumulative share of records. Ranks names by frequency so hand-labelling effort goes where it covers most records (103 names reach 85%) |
| 7 | `label_lenders.py` | Assigns every clean name a parent group (by current owner, e.g. Silicon Valley Bank UK under HSBC) and a type: bank, debt fund, agent/trustee, sponsor, government, property investor, specialist non-bank, individual, other or unresolved. Hand decisions come first, for frequent names and then the long tail, each written in the script so it can be checked line by line. Keyword rules handle the rest, and anything left is reported as unresolved rather than dropped |
| 8 | `summarise.py` | Produces the summary tables in `results.txt` |

## Results so far

Sample: 300 companies, 150 care and 150 software, drawn from 1,655 mid-market companies with at least one charge. Full output is in `results.txt`.

**Data**

| | |
|---|---|
| Distinct charges | 2,363 |
| Lender-charge rows | 2,385 |
| Companies whose downloaded charge count matches the bulk file | 299 of 300 |
| Distinct raw lender names | 562 |
| Distinct names after cleaning | 388 |
| Names covering 85% of records | 103 |

**Headline findings**

Non-bank lender here means debt fund, specialist non-bank lender or property investor. Sponsors, government, individuals, agents and trustees are reported separately.

1. **Banks still dominate the register.** 70% of lender records are banks, and five groups (NatWest, Barclays, HSBC, Lloyds, Virgin Money) hold 67.7% of identified lender-charge links.
2. **Debt funds show up in software, not in care.** 20.0% of software companies have at least one debt fund charge, against 1.3% of care companies.
3. **Non-bank lending in care comes from somewhere other than credit funds.** 10.0% of care companies have a non-bank lender, but only 1.3% have a debt fund. The rest are property investors (such as HCP / Healthpeak, Welltower and Omega) and specialist non-bank lenders.
4. **The shift is recent, and differs by sector.** Charges with a non-bank lender:

| Period | Care (%) | Software (%) |
|---|---|---|
| pre-2013 | 0.6 | 0.7 |
| 2013-2019 | 17.0 | 14.1 |
| 2020+ | 5.9 | 20.9 |

   In software, the non-bank share keeps rising. In care, it peaked in 2013-2019 and fell back. These are charge-level shares, so a few borrowers with many charges can move them.

**How much the unresolved names could matter**

Share of companies with a non-bank lender:

| | Care (%) | Software (%) |
|---|---|---|
| If all unresolved names are banks | 10.0 | 25.3 |
| If all unresolved names are non-banks | 28.0 | 38.7 |

The true figure lies between these bounds. Resolving the remaining names would narrow it.

## Data in this repository

The Companies House bulk file is not included because it is too large. Download it as described under Pipeline. Everything the scripts produce from it is included, so results can be checked without re-running the download:

- `data/sample.csv`: the 300 sample companies
- `data/charges/`: raw charge records from the API, one JSON file per company
- `data/lender_map.csv`: every clean lender name with its parent, type and the reason for the label
- `results.txt`: output of `summarise.py`

## Setup

```bash
git clone https://github.com/<HeXlo-9>/uk-private-credit-linkage.git
cd uk-private-credit-linkage
pip install -r requirements.txt
```

Requires Python 3.9+ with `requests` and `pandas`.

You need a free Companies House API key from the [Companies House developer hub](https://developer.company-information.service.gov.uk/). Store it as an environment variable rather than in the code:

```bash
export CH_API_KEY="your-key-here"
```

## Known limitations

- **Registered secured lending only.** Unsecured debt, borrowing at Luxembourg or other offshore holding companies, and fund-level facilities do not show up in the register.
- **Security agents hide lenders.** 6.3% of records name an agent or trustee (for example GLAS, Wilmington Trust, Kroll) rather than the lender itself. These are common in sponsor-backed and direct lending deals, so the debt fund share is likely understated.
- **The sample only includes companies with charges.** Shares describe who lends to companies that borrow on a secured basis, not to the mid-market as a whole.
- **Account category is a size proxy.** FULL, GROUP or MEDIUM accounts usually mean a company is above the small-company thresholds, but a small company can choose to file full accounts.
- **Shares include satisfied charges.** Repaid and released charges are counted alongside outstanding ones. The period split shows when charges were created, not whether the lending is still in place.
- **Banks acting as agents count as banks.** Cleaning removes the "as security agent for ..." wording, so a bank that holds security for a syndicate is labelled as the bank. The role is kept in `lender_role` but not yet used in the summary.
- **Charges are not loans.** A charge shows that a lender holds security, not the size, pricing or terms of the loan.
- **Labels are hand decisions plus keyword rules.** 5.2% of records remain unresolved. Keyword rules can misfire on names that happen to contain the keyword.
- **Two sectors, one country.** Care and software are not the whole mid-market, and the UK does not transfer directly to Germany, Austria or Switzerland.

## Possible second phase

A hand-collected sample of German companies from the Unternehmensregister, tracking Verbindlichkeiten gegenüber Kreditinstituten (liabilities to banks) against other financial liabilities, as an indirect signal of non-bank lending.

## Author

Prathish Shetty, M.Sc. Finance, Frankfurt School of Finance & Management