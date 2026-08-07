import streamlit as st
import re

from ai_engine import generate_sql, generate_answer
from sql_helper import run_query

def format_large_numbers(text):

    def format_number(match):

        number = float(match.group(0).replace(",", ""))

        if abs(number) >= 1_000_000_000:
            return f"{number / 1_000_000_000:.1f}B"

        elif abs(number) >= 1_000_000:
            return f"{number / 1_000_000:.1f}M"

        elif abs(number) >= 10_000:
            return f"{number / 1_000:.1f}K"

        return match.group(0)


    return re.sub(
        r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?|\b\d+(?:\.\d+)?\b",
        format_number,
        text
    )


st.set_page_config(
    page_title="Insurance AI Assistant",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ Insurance AI Assistant")
st.caption("Ask questions about your insurance analytics data")


if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
question = st.chat_input("Ask something about your insurance data...")


if question:

    # User message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Assistant response
    with st.chat_message("assistant"):

        try:
            with st.spinner("Analyzing your data..."):

                # AI → SQL
                sql = generate_sql(question)

                # SQL → Fabric
                columns, rows = run_query(sql)

                # Result → human answer
                answer = generate_answer(
                    question,
                    columns,
                    rows
                )

                print("RAW AI ANSWER:", answer)

                formatted_answer = format_large_numbers(answer)

                print("FORMATTED ANSWER:", formatted_answer)

                st.markdown(formatted_answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": formatted_answer
                })

        except Exception as e:

            error_message = (
                f"Sorry, I couldn't process that question.\n\n`{e}`"
            )

            st.error(error_message)

            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })