"""
Step 7: assign every cleaned lender name a parent group and a type.

Order of decisions:
  1. hand decisions for the most frequent names (MANUAL)
  2. hand decisions for the long tail (TAIL)
  3. rules: agent/trustee words, public-sector words, known banking groups, "bank"/"building society"
  4. anything else -> "unresolved" (reported, not dropped)

Every hand decision is written here so it can be checked and challenged line by line.
Parents are grouped by current owner (e.g. Silicon Valley Bank UK under HSBC).

Input:  data/lender_list.csv
Output: data/lender_map.csv
"""
import pandas as pd

lenders = pd.read_csv("data/lender_list.csv", dtype=str).fillna("")

# known banking groups: (text in cleaned name, parent)
BANK_GROUPS = [
    ("barclays", "Barclays"), ("woolwich", "Barclays"),
    ("national westminster", "NatWest Group"), ("royal bank of scotland", "NatWest Group"),
    ("coutts", "NatWest Group"),
    ("lloyds", "Lloyds Banking Group"), ("bank of scotland", "Lloyds Banking Group"),  # after RBS, so RBS matches first
    ("hsbc", "HSBC"), ("midland bank", "HSBC"), ("silicon valley bank", "HSBC"),
    ("clydesdale", "Virgin Money"), ("yorkshire bank", "Virgin Money"), ("virgin money", "Virgin Money"),
    ("santander", "Santander"), ("abbey national", "Santander"), ("alliance and leicester", "Santander"),
    ("nationwide", "Nationwide"),
    ("bank of ireland", "Bank of Ireland"),
    ("aib group", "AIB"), ("allied irish", "AIB"),
]

# words marking a security agent or trustee (checked before banks)
AGENT_WORDS = ["security trustee", "corporate trustee", "trustee services", "trust corporation",
               "security agent", "collateral agent", "administrative agent",
               "mount street", "wilmington trust", "glas "]

# words marking the public sector
GOV_WORDS = ["council", "health authority", "secretary of state", "nhs", "borough"]

# hand decisions for the most frequent names: cleaned name -> (parent, type, note)
MANUAL = {
    "hcp":                                    ("HCP / Healthpeak", "property_investor", "US healthcare property investor"),
    "hcp uk investments":                     ("HCP / Healthpeak", "property_investor", ""),
    "sixth street lending partners":          ("Sixth Street", "debt_fund", "US direct lending fund"),
    "credit suisse first boston":             ("UBS (Credit Suisse)", "bank", "Credit Suisse acquired by UBS 2023"),
    "credit suisse cayman islands branch":    ("UBS (Credit Suisse)", "bank", ""),
    "ubs stamford branch":                    ("UBS", "agent_trustee", "bank acting as agent for a syndicate"),
    "paragon business finance":               ("Paragon Banking Group", "bank", ""),
    "close brothers":                         ("Close Brothers", "bank", ""),
    "abbey national":                         ("Santander", "bank", "predecessor of Santander UK"),
    "alliance and leicester":                 ("Santander", "bank", "acquired by Santander"),
    "bristol and west building society":      ("Bank of Ireland", "bank", "acquired by Bank of Ireland"),
    "northern rock":                          ("Virgin Money", "bank", ""),
    "tpg speciality lending europe i advisors": ("Sixth Street", "debt_fund", "TPG Specialty Lending, now Sixth Street"),
    "crestline direct finance l p":           ("Crestline", "debt_fund", "fund manager as agent for own funds"),
    "bain capital credit":                    ("Bain Capital Credit", "debt_fund", "fund manager as agent for own funds"),
    "downing":                                ("Downing", "debt_fund", "fund manager as agent for own funds"),
    "triplepoint capital llc":                ("TriplePoint Capital", "debt_fund", "US venture debt; NOT Triple Point UK"),
    "kreos capital vii":                      ("Kreos", "debt_fund", "venture debt"),
    "triple point lease partners":            ("Triple Point", "specialist_nonbank", "UK asset finance; NOT TriplePoint Capital"),
    "fundsquire":                             ("Fundsquire", "specialist_nonbank", ""),
    "humberclyde finance group":              ("Humberclyde", "specialist_nonbank", "asset finance"),
    "cbre loan services":                     ("CBRE", "agent_trustee", "loan servicer"),
    "situs asset management":                 ("Situs", "agent_trustee", "loan servicer"),
    "solutus advisors":                       ("Solutus", "agent_trustee", "loan servicer"),
    "alter domus trustees":                   ("Alter Domus", "agent_trustee", ""),
    "phoenix equity nominees":                ("Phoenix Equity", "sponsor", "PE investor"),
    "northedge capital":                      ("Northedge", "sponsor", "PE investor"),
    "northedge capital nominee":              ("Northedge", "sponsor", "PE investor"),
    "ldc":                                    ("Lloyds Banking Group", "sponsor", "LDC = Lloyds' PE arm"),
    "bgf nominees":                           ("BGF", "sponsor", "growth equity investor"),
    "soho square capital":                    ("Soho Square", "sponsor", "PE investor"),
    "accel europe l p":                       ("Accel", "sponsor", "VC investor"),
    "interregnum":                            ("Interregnum", "sponsor", "tech venture investor"),
    "housing corporation":                    ("Housing Corporation", "government", ""),
    "finance wales investments":              ("Development Bank of Wales", "government", ""),
    "amber meef 2":                           ("Midlands Engine Investment Fund", "government", "public-backed fund"),
    "mercian housing association":            ("Mercian Housing Association", "other", "landlord"),
    "trident housing association":            ("Trident Housing Association", "other", "landlord"),
    "university of surrey":                   ("University of Surrey", "other", "landlord"),
    "rowanmoor trustees":                     ("Rowanmoor", "other", "pension scheme trustee"),
    "shell care holdco":                      ("Shell Care Holdco", "other", "own parent company"),
    "correlation one holdings":               ("Correlation One", "other", "likely acquirer or parent"),
    "ucb bank":                               ("UCB", "unresolved", "rule said bank; owner to check"),
}

# hand decisions for the long tail, grouped by type
TAIL = {
    "debt_fund": [
        "lendable asset management llc", "ab private credit investors llc", "salica growth debt fund i spv",
        "growth lending 2021", "growth lending 2020", "tpg specialty lending", "bock senior capital investors iv s r l",
        "ubp private debt fund iii designated activity company", "eastward fund management llc",
        "eastward capital partners v l p", "sixth street specialty lending",
        "sixth street specialty lending europe ii advisors", "riverside acceleration capital fund ii l p",
        "bluebay ireland corporate credit i", "ares management", "ares management acting", "kreos capital vi",
        "golub capital markets llc", "hercules capital", "eldridge corporate funding llc",
        "crestline direct finance l p as secured party", "bootstrap europe 2 0", "etv capital s a",
    ],
    "specialist_nonbank": [
        "marketinvoice", "assetz capital trust company", "time invoice finance", "bibby financial services",
        "capify uk llc", "peac business finance", "hyundai capital uk", "lancashire mortgage corporation",
        "black country reinvestment society", "newable management services",
    ],
    "bank": [
        "cynergy business finance", "close leasing", "lombard north central", "rbs invoice finance",
        "alex lawrie receivables financing", "royscot trust", "abn amro commercial finance",
        "arbuthnot commercial asset based lending", "arbuthnot latham and co", "wells fargo capital finance llc",
        "wells fargo foothill", "well fargo foothill", "natwest markets", "credit suisse london branch",
    ],
    "property_investor": [
        "nhp securities no 3", "hcn finco trs", "ohi uk lender llc", "civitas social housing", "caretrust uk",
    ],
    "sponsor": [
        "westbridge ii", "westbridge fund managers", "livingbridge enterprise", "eci ventures nominees",
        "phoenix equity partners", "3i group", "trinity venture capital", "xplorer capital fund v",
        "tenzing private equity", "matrix private equity partners", "catapult growth fund partnership",
        "palatine gc holdings",
    ],
    "government": [
        "scottish enterprise", "creative england",
        "merseyside special investments mezzanine no 2 acting by its general partner afm merseysidemezzanine",
    ],
    "agent_trustee": [
        "ocorian trustee", "alter domus credit administration acting", "project finance investments",
    ],
    "individual": [
        "jeremy griffin beasley", "john richmond beasley", "j r beasley", "j n beasley", "david mark hunter",
        "andrew vincent", "r nicholson", "r d read", "h m read", "paul bignell", "timothy bignell",
        "valerie bignell", "w lawrence", "stephen nicholas kingan", "stephen rau stone and dawn sandra stone",
        "christopher ian farrelly", "d j medlock", "b n medlock", "l medlock", "david dixon",
        "alecwilliam bates", "alec william bates and josephine bates", "michael anthony bates", "alan howard",
        "alan cambridge", "a collins", "joseph pearlman", "j thorne", "benjamin white", "konrad czajka",
        "mitchell barney", "michael kristian odling smee and joseph samuel waller",
        "michael webber and ronald michael harris", "mr m p elson", "nigel gregg fasey",
        "geoffrey norman john davis", "g yukes", "flora clifton white", "emanuel mond", "george lightfoot",
        "graham ransom", "sellers",
    ],
    "other": [
        # pension schemes of owners or directors
        "john colwell", "adrian john otten", "carol ann braddick", "graham bruce moss",
        "john colwell and adrian otten as trustees of the colten development pension scheme",
        "john colwell and adrian otten and rowanmoor trustees",
        "mr john colwell and mr adrian john otten and rowanmoor trustees as trustees of the colten developments pension scheme",
        "david mark hunter and barnett waddingham capital trustees as trustees of the dmhexecutive trust funded unapproved retirement scheme",
        "andrew vincent and barnett waddingham capital trustees as trustees of the av executivetrust funded unapproved retirement scheme",
        "central tax and trustee planning", "threadneedle pensions",
        # landlords and property companies
        "industrial property investment fund", "porthaven properties", "oakmede developments",
        "beechcroft developments", "mitchell properties", "willowbrook properties holdco", "theta properties",
        "chartmoor estates", "bond s mill estate", "bruntwood 2000 first properties",
        "derwent valley property developments", "eric wright developments", "p and o property holdings",
        "hammersmith grove nominee no 1 hammersmith grove nominee no 2", "wbp", "lms",
        "letchworth garden city heritage foundation", "mayor and commonalty and citizens of the city of london",
        "master fellows and scholars of churchill college in cambridge", "darrington healthcare properties",
        # trading counterparties, sellers, own group
        "universal studios holdings", "refinitiv uk parent", "refinitiv us llc", "carnival", "xerox",
        "alcan holdings uk", "enterprise oil", "bauer consumer media", "curve digital entertainment",
        "carter thermal industries", "capital markets company", "bic", "vernalis", "correlation one investments",
        "revera uk holdings", "country court care homes 3 opco", "community integrated care",
        "quercus nursing homes 2001 and quercus nursing homes 2001", "quercus",
    ],
}

# tail names that belong to a group already named elsewhere
TAIL_PARENT = {
    "tpg specialty lending": "Sixth Street", "sixth street specialty lending": "Sixth Street",
    "sixth street specialty lending europe ii advisors": "Sixth Street",
    "eastward fund management llc": "Eastward", "eastward capital partners v l p": "Eastward",
    "ares management": "Ares", "ares management acting": "Ares", "kreos capital vi": "Kreos",
    "crestline direct finance l p as secured party": "Crestline",
    "growth lending 2021": "Growth Lending", "growth lending 2020": "Growth Lending",
    "westbridge ii": "Westbridge", "westbridge fund managers": "Westbridge",
    "phoenix equity partners": "Phoenix Equity", "close leasing": "Close Brothers",
    "lombard north central": "NatWest Group", "rbs invoice finance": "NatWest Group",
    "royscot trust": "NatWest Group", "natwest markets": "NatWest Group",
    "alex lawrie receivables financing": "Lloyds Banking Group",
    "credit suisse london branch": "UBS (Credit Suisse)",
    "wells fargo capital finance llc": "Wells Fargo", "wells fargo foothill": "Wells Fargo",
    "well fargo foothill": "Wells Fargo", "arbuthnot commercial asset based lending": "Arbuthnot",
    "arbuthnot latham and co": "Arbuthnot", "alter domus credit administration acting": "Alter Domus",
    "hcn finco trs": "Welltower (Health Care REIT)", "ohi uk lender llc": "Omega Healthcare",
    "nhp securities no 3": "NHP", "correlation one investments": "Correlation One",
}
TAIL_TYPE = {name: t for t, names in TAIL.items() for name in names}


def label(name):
    if name in MANUAL:                                       # 1. hand decisions, frequent names
        return MANUAL[name]
    if name in TAIL_TYPE:                                    # 2. hand decisions, tail
        return (TAIL_PARENT.get(name, name), TAIL_TYPE[name], "tail: hand decision")
    parent = next((p for text, p in BANK_GROUPS if text in name), "")
    if any(w in name for w in AGENT_WORDS):                  # 3. agents and trustees
        return (parent or name, "agent_trustee", "rule: agent/trustee word")
    if any(w in name for w in GOV_WORDS):                    # 4. public sector
        return (name, "government", "rule: public sector word")
    if parent:                                               # 5. known banking groups
        return (parent, "bank", "rule: bank group")
    if "bank" in name or "building society" in name:         # 6. other banks
        return (name, "bank", "rule: bank or building society")
    return (name, "unresolved", "not identified")            # 7. everything else


lenders[["parent", "type", "notes"]] = lenders["lender_clean"].apply(lambda n: pd.Series(label(n)))
lenders.to_csv("data/lender_map.csv", index=False)

rows = lenders["rows"].astype(int)
print("Names by type:")
print(lenders["type"].value_counts())
print("\nShare of lender records by type (%):")
print((rows.groupby(lenders["type"]).sum() / rows.sum() * 100).round(1).sort_values(ascending=False))