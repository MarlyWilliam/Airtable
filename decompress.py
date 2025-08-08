import json, os
from dotenv import load_dotenv
from pyairtable import Api

# Load API keys
load_dotenv()
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
API_KEY = os.getenv("AIRTABLE_API_KEY")

# Airtable setup
api = Api(API_KEY)
tbl_applicants = api.table(BASE_ID, "Applicants")
tbl_personal   = api.table(BASE_ID, "Personal Details")
tbl_experience = api.table(BASE_ID, "Work Experience")
tbl_salary     = api.table(BASE_ID, "Salary Preferences")

# Helper: get linked child records
def get_linked_records(table, applicant_id):
    return [
        r for r in table.all()
        if applicant_id in r.get("fields", {}).get("Applicant", [])
    ]

# Sync Personal Details (one-to-one)
def sync_personal(applicant_id, personal):
    if not personal: return
    mapped = {
        "Full Name": personal.get("name"),
        "Location": personal.get("location"),
        "Applicant": [applicant_id],
    }
    existing = get_linked_records(tbl_personal, applicant_id)
    if existing:
        tbl_personal.update(existing[0]["id"], mapped)
    else:
        tbl_personal.create(mapped)

# Sync Salary Preferences (one-to-one)
def sync_salary(applicant_id, salary):
    if not salary: return
    mapped = {
        "Preferred Rate": salary.get("rate"),
        "Currency": salary.get("currency"),
        "Availability": salary.get("availability"),
        "Applicant": [applicant_id],
    }
    existing = get_linked_records(tbl_salary, applicant_id)
    if existing:
        tbl_salary.update(existing[0]["id"], mapped)
    else:
        tbl_salary.create(mapped)

# Sync Work Experience (one-to-many)
def sync_experience(applicant_id, experiences):
    if not experiences: return
    existing = get_linked_records(tbl_experience, applicant_id)
    for rec in existing:
        tbl_experience.delete(rec["id"])
    for exp in experiences:
        tbl_experience.create({
            "Company": exp.get("company"),
            "Title": exp.get("title"),
            "Applicant": [applicant_id],
            "Start": exp.get("start"),
            "End": exp.get("end"),
        })

# Main loop: read each JSON and sync
for applicant in tbl_applicants.all():
    blob = applicant["fields"].get("Compressed JSON")
    if not blob:
        print(f"⚠️  No JSON for {applicant['id']}")
        continue
    try:
        data = json.loads(blob)
    except Exception as e:
        print(f"❌ JSON error for {applicant['id']}: {e}")
        continue

    applicant_id = applicant["id"]
    sync_personal(applicant_id, data.get("personal"))
    sync_salary(applicant_id, data.get("salary"))
    sync_experience(applicant_id, data.get("experience"))
