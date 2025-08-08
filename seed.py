# seed_candidates.py
import os
from dotenv import load_dotenv
from pyairtable import Table
load_dotenv()

API, BASE = os.getenv("AIRTABLE_API_KEY"), os.getenv("AIRTABLE_BASE_ID")

tbl_app = Table(API, BASE, "Applicants")
tbl_p   = Table(API, BASE, "Personal Details")
tbl_e   = Table(API, BASE, "Work Experience")
tbl_s   = Table(API, BASE, "Salary Preferences")

# Helper to link: Airtable link fields expect a list of record IDs
def link(rec_id): return [rec_id]

# --- Candidate A (should PASS) ---
a = tbl_app.create({"Name": "Jane Qualified"})
a_id = a["id"]

tbl_p.create({
  "Full Name": "Jane Qualified",
  "Applicant": link(a_id),
  "Email": "jane@example.com",
  "Location": "New York, US",
  "LinkedIn": "https://linkedin.com/in/janeq"
})

tbl_e.create({
  "Applicant": link(a_id),
  "Company": "Google",
  "Title": "Software Engineer",
  "Start": "2019-01-01",
  "End": "2023-12-31"
})
tbl_e.create({
  "Applicant": link(a_id),
  "Company": "Acme Co",
  "Title": "Senior SWE",
  "Start": "2024-01-01",
  "End": "2025-01-01"
})

tbl_s.create({
  "Label": "Main",
  "Applicant": link(a_id),
  "Preferred Rate": 95,     # <= 100
  "Minimum Rate": 80,
  "Currency": "USD",
  "Availability": 25        # >= 20
})

# --- Candidate B (should FAIL) ---
b = tbl_app.create({"Name": "John NotReady"})
b_id = b["id"]

tbl_p.create({
  "Full Name": "John NotReady",
  "Applicant": link(b_id),
  "Email": "john@example.com",
  "Location": "Cairo, Egypt",
})

tbl_e.create({
  "Applicant": link(b_id),
  "Company": "Local Startup",
  "Title": "Dev",
  "Start": "2022-01-01",
  "End": "2023-01-01"
})

tbl_s.create({
  "Label": "Main",
  "Applicant": link(b_id),
  "Preferred Rate": 120,    # > 100
  "Minimum Rate": 100,
  "Currency": "USD",
  "Availability": 10        # < 20
})

print("Seeded candidates.")
