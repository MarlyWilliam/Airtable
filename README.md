LLM Evaluation & Shortlisting System
1. Overview
This system integrates Airtable with a modern LLM (such as OpenAI or DeepSeek) to streamline candidate evaluation, summarization, and shortlisting. It automates structured JSON generation, rule-based filtering, and qualitative review via LLMs.
2. Setup Steps
2.1 Prerequisites
Python 3.10+


Airtable base with required schema


Airtable API key and base ID


OpenRouter or OpenAI API key (for LLM calls)


2.2 Environment Variables
Create a .env file in your root directory with the following:
AIRTABLE_API_KEY=your_airtable_key
AIRTABLE_BASE_ID=your_base_id
DEEPSEEK_API_KEY=your_openrouter_key

Install dependencies:
pip install python-dotenv pyairtable requests

3. Field Definitions
3.1 Applicants
The central table that holds core candidate data.
Field Name
Description
Name
Applicant's short name
Compressed JSON
Combined data from linked tables
JSON Hash
MD5 hash to detect changes
LLM Summary
Generated text summary
LLM Score
Score from 1–10
LLM Follow-Ups
Follow-up questions from LLM

3.2 Personal Details
Field Name
Description
Full Name
Full name of the applicant
Email
Email address
Location
City and Country (e.g., "New York, US")
LinkedIn
LinkedIn profile URL
Applicant
Link to Applicants table

3.3 Work Experience
Field Name
Description
Company
Company name (e.g., Google)
Title
Job title
Start
Start date (YYYY-MM-DD)
End
End date (YYYY-MM-DD or null)
Applicant
Link to Applicants table

3.4 Salary Preferences
Field Name
Description
ID


Preferred Rate
Desired rate (≤ 100 USD)
Minimum Rate
Lowest acceptable rate
Currency
Currency (e.g., USD)
Availability
Percent availability (≥ 20)
Applicant
Link to Applicants table

3.5 Tier 1 Companies
Field Name
Description
Name
Company name (e.g., Google, Meta)

3.6 Allowed Countries
Field Name
Description
Name
Country (e.g., United States, Canada)

3.7 Shortlisted Leads
Field Name
Description
Name
Candidate name
Source
Usually "Main"
Applicant
Link to Applicants
Companies
List of past employers

4. Automations
4.1 Compression Script (compress.py)
Combines fields from Personal Details, Work Experience, and Salary Preferences into a single JSON blob and stores it in the Compressed JSON field of Applicants.
4.2 Shortlisting Script (shortlist.py)
Checks if:
Any experience includes a Tier 1 company


Location matches one of the Allowed Countries


Salary and availability are within acceptable thresholds


If all pass, the applicant is added to the Shortlisted Leads table.
4.3 Enrichment Script (llm_enrich.py)
Uses an LLM to:
Generate a summary


Assign a quality score (1–10)


Flag issues or inconsistencies


Propose follow-up questions


Skips API call if the input JSON has not changed.
5. LLM Integration
5.1 Prompt Template
You are a recruiting analyst. Given this JSON profile:
{json}

1. Summarize in ≤75 words.
2. Score 1–10.
3. List any gaps/inconsistencies.
4. Suggest up to 3 follow-up questions.

Reply with:
Summary: <text>
Score: <int>
Issues: <text>
Follow-Ups: <bullet list>

5.2 DeepSeek API Usage
The script calls https://openrouter.ai/api/v1/chat/completions with:
Model: deepseek/deepseek-r1:free


Bearer token from .env


temperature = 0.2, max_tokens = 500


5.3 Error Handling
Retries up to 3 times using exponential backoff


Falls back to defaults on parsing errors


5.4 Output Fields
Results are stored in LLM Summary, LLM Score, and LLM Follow-Ups.
6. Extending Shortlist Criteria
To adjust filtering logic:
Modify shortlist.py


Update company or location whitelists via Airtable


Add more rules as needed (e.g., years of experience, skill keywords)


7. Deliverables
Airtable base with the 7 required tables


Seed script: seed.py


Scripts: compress.py, shortlist.py, llm_enrich.py


.env file for credentials



