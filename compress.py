import json, os
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
API_KEY = os.getenv("AIRTABLE_API_KEY")

api = Api(API_KEY)
tbl_applicants = api.table(BASE_ID, "Applicants")
tbl_personal   = api.table(BASE_ID, "Personal Details")
tbl_experience = api.table(BASE_ID, "Work Experience")
tbl_salary     = api.table(BASE_ID, "Salary Preferences")

def link_formula(link_field: str, parent_id: str) -> str:
    return f"FIND('{parent_id}', ARRAYJOIN({{{link_field}}})) > 0"

def bundle(applicant_id: str) -> str:
    # Fetch all data and filter in Python
    all_personal = tbl_personal.all()
    all_salary   = tbl_salary.all()
    all_exp      = tbl_experience.all()

    personal = next(
        (r["fields"] for r in all_personal
         if applicant_id in r.get("fields", {}).get("Applicant", [])), {}
    )
    salary = next(
        (r["fields"] for r in all_salary
         if applicant_id in r.get("fields", {}).get("Applicant", [])), {}
    )
    experience = [
        r["fields"] for r in all_exp
        if applicant_id in r.get("fields", {}).get("Applicant", [])
    ]

    personal_json = {
        "name": personal.get("Full Name"),
        "location": personal.get("Location"),
    }

    experience_json = [
        {
            "company": e.get("Company"),
            "title": e.get("Title"),
            "start": e.get("Start"),
            "end": e.get("End"),
        }
        for e in experience
    ]

    salary_json = {
        "rate": salary.get("Preferred Rate"),
        "currency": salary.get("Currency"),
        "availability": salary.get("Availability"),
    }

    return json.dumps({
        "personal": personal_json,
        "experience": experience_json,
        "salary": salary_json
    }, default=str)


for rec in tbl_applicants.all():
    blob = bundle(rec["id"])
    tbl_applicants.update(rec["id"], {"Compressed JSON": blob})
