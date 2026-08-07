import os
from dotenv import load_dotenv
from groq import Groq

from schema import SCHEMA

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


SYSTEM_PROMPT = f"""
{SCHEMA}

You are an AI assistant for an Insurance Analytics dashboard.

Your job is to convert the user's natural-language question
into ONE safe SQL SELECT query.

Rules:

1. Use ONLY tables and columns defined in the schema.
2. Never invent columns or tables.
3. Use SQL Server / Fabric SQL syntax.
4. Generate ONLY SELECT statements.
5. Never use INSERT, UPDATE, DELETE, DROP, ALTER or TRUNCATE.
6. For date questions, use the actual date columns available.
7. For "this month", determine the current month from the available date data.
8. For monthly analysis, use claim_date/event_date as appropriate.
9. Return only the SQL query.
10. Do not put the SQL inside markdown code fences.

Examples:

User:
"How many claims are there?"

SQL:
SELECT SUM(total_claims) AS total_claims
FROM dbo.gold_claims_summary;

User:
"What is the average claim amount?"

SQL:
SELECT AVG(avg_claim_amount) AS average_claim_amount
FROM dbo.gold_claims_summary;

User:
"How many rejected claims are there?"

SQL:
SELECT SUM(total_claims) AS rejected_claims
FROM dbo.gold_claims_summary
WHERE claim_status = 'REJECTED';

User:
"Which cities have high risk?"

SQL:
SELECT city, city_risk_level, total_claims, total_claim_amount
FROM dbo.gold_city_risk
WHERE city_risk_level = 'HIGH';

Now convert the user's question into SQL.
"""


def generate_sql(question):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    # Remove accidental markdown fences
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql

def generate_answer(question, columns, rows):
    result_text = []

    for row in rows:
        result_text.append(
            ", ".join(
                f"{columns[i]} = {row[i]}"
                for i in range(len(columns))
            )
        )

    result_text = "\n".join(result_text)

    prompt = f"""
You are an AI assistant for an Insurance Analytics project.

Answer the user's question using ONLY the database result provided below.

User question:
{question}

Database result:
{result_text}

Rules:
- Give a clear, concise answer.
- Do not invent information.
- Do not mention SQL or database technical details unless necessary.
- Include the relevant number/date/category in the answer.
- If the result contains one number, explain what that number represents.
- Always keep numeric values as digits, never write numbers in words.
- Keep exact database values unchanged.
- Number formatting will be handled separately.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You answer insurance analytics questions using database results."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()