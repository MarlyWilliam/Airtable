import hashlib
import os
import requests
from dotenv import load_dotenv
from pyairtable import Table

# Load environment variables
load_dotenv()

# Airtable and LLM configuration
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
API_KEY = os.getenv("AIRTABLE_API_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
LLM_URL = "https://openrouter.ai/api/v1/chat/completions"

# Airtable table
tbl_applicants = Table(API_KEY, BASE_ID, "Applicants")

# LLM Prompt Template
TEMPLATE = """You are a recruiting analyst. Given this JSON profile:
{json}

1. Summarize in ≤75 words.
2. Score 1-10.
3. List any gaps/inconsistencies.
4. Suggest up to 3 follow-up questions.

Reply with:
Summary: <text>
Score: <int>
Issues: <text>
Follow-Ups: <bullet list>
"""

def ask_deepseek(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 500
    }
    res = requests.post(LLM_URL, headers=headers, json=payload)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

for rec in tbl_applicants.all():
    blob = rec["fields"].get("Compressed JSON")
    if not blob:
        continue

    md5 = hashlib.md5(blob.encode()).hexdigest()
    
    # Skip if unchanged (optional)
    if rec["fields"].get("JSON Hash") == md5:
        continue

    prompt = TEMPLATE.format(json=blob)

    try:
        raw_reply = ask_deepseek(prompt)
        print(f"\n🔍 Raw LLM Response:\n{raw_reply}\n")

        # Parse LLM Response
        reply = raw_reply.splitlines()
        summary, score, issues, follow_lines = "", 0, "", []

        for i, line in enumerate(reply):
            line = line.strip()
            if line.startswith("Summary:"):
                summary = line.split(":", 1)[1].strip()
            elif line.startswith("Score:"):
                try:
                    score = int(line.split(":", 1)[1].strip())
                except:
                    score = 0
            elif line.startswith("Issues:"):
                issues = line.split(":", 1)[1].strip()
            elif line.startswith("Follow-Ups:"):
                follow_lines.append(line.split(":", 1)[1].strip())
                for f_line in reply[i+1:]:
                    f_line = f_line.strip()
                    if f_line.startswith(("•", "-", "*")):
                        follow_lines.append(f_line)
                    else:
                        break

        follow = "\n".join(follow_lines).strip()

        # Update Airtable record
        tbl_applicants.update(rec["id"], {
            "LLM Summary":     summary,
            "LLM Score":       score,
            "LLM Follow-Ups":  follow,
            "JSON Hash":       md5
        })

        print(f"✅ Updated: {rec['fields'].get('Full Name', rec['id'])} | Score: {score}")

    except Exception as e:
        print(f"❌ Failed on {rec['id']}: {e}")
