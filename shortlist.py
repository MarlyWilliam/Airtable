"""
Applies three simple rules to decide whether an applicant
should be shortlisted.  If yes, creates a row in Shortlisted Leads.
"""

import json, os
from dotenv import load_dotenv
from pyairtable import Table

load_dotenv()
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
API_KEY = os.getenv("AIRTABLE_API_KEY")

tbl_applicants = Table(API_KEY, BASE_ID, "Applicants")
tbl_shortlist  = Table(API_KEY, BASE_ID, "Shortlisted Leads")
tier1          = {r["fields"]["Company"] for r in Table(API_KEY, BASE_ID,
                   "Helper - Tier-1 Companies").all()}
allowed_locs   = {r["fields"]["Country"] for r in Table(API_KEY, BASE_ID,
                   "Helper - Allowed Locations").all()}


def passes_rules(profile: dict) -> tuple[bool, str]:
    # Calculate years of experience
    yrs = 0
    for e in profile["experience"]:
        try:
            start = int(e.get("start", "")[:4])
            end = int(e.get("End", "")[:4])
            if start and end:
                yrs += end - start
        except ValueError:
            continue

    # Rule: Tier-1 experience
    big_co = any(e.get("company") in tier1 for e in profile["experience"])
    exp_ok = yrs >= 4 or big_co

    # Rule: Salary + availability
    sal = profile["salary"]
    comp_ok = sal.get("rate", 9999) <= 100 and sal.get("availability", 0) >= 20

    # Rule: Location
    loc = profile["personal"].get("location", "")
    country = loc.split(",")[-1].strip()
    loc_ok = country in allowed_locs

    # Collect reasons
    reasons = []
    if exp_ok:  reasons.append("experience")
    if comp_ok: reasons.append("rate/availability")
    if loc_ok:  reasons.append("location")

    return (len(reasons) == 3, ", ".join(reasons))



for rec in tbl_applicants.all():
    data = json.loads(rec["fields"]["Compressed JSON"])
    ok, reason = passes_rules(data)
    
    print(f"\n🧪 Applicant: {rec['fields'].get('Full Name', rec['id'])}")
    print(f"Passes rules: {ok} | Reason: {reason}")
    
    if ok and rec["fields"].get("Shortlist Status") != "Shortlisted":
        tbl_shortlist.create({
            "Applicant": [rec["id"]],
            "Compressed JSON": rec["fields"]["Compressed JSON"],
            "Score Reason": reason
        })
        tbl_applicants.update(rec["id"], {"Shortlist Status": "Shortlisted"})

