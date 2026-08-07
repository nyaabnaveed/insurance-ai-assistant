from ai_engine import generate_sql, generate_answer
from sql_helper import run_query
from app import format_large_numbers

question = "How many rejected claims are there?"

try:

    # AI → SQL
    sql = generate_sql(question)

    print("🤖 Generated SQL:")
    print(sql)

    # SQL → Fabric
    columns, rows = run_query(sql)

    # Result → Human answer
    answer = generate_answer(
        question,
        columns,
        rows
    )

    # Format numbers
    formatted_answer = format_large_numbers(answer)

    print("\n💬 AI Answer:")
    print(formatted_answer)

except Exception as e:

    print("\n❌ Error:")
    print(e)