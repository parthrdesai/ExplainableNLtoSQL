import streamlit as st
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

SCHEMA = """
Tables:
Customers(id INT, name TEXT, age INT, city TEXT)
Orders(order_id INT, customer_id INT, amount FLOAT, date TEXT)
"""

def call_ollama(prompt):
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    res = requests.post(OLLAMA_URL, json=payload)
    return res.json()['response']


def generate_sql_and_explanation(query):
    prompt = f"""
You are a NL2SQL assistant with EXPLANATION ability.

Given this schema:
{SCHEMA}

User question: "{query}"

Your output MUST have EXACTLY these blocks in this order and MUST STOP after END_MAPPING:

BEGIN_SQL
<SQL QUERY HERE>
END_SQL

BEGIN_EXPLANATION
<Explain briefly:>
- which tables are used
- which conditions were created
- how each phrase was understood.
END_EXPLANATION

BEGIN_MAPPING
Use bullet list, each on its own line, EXACT format:
- "phrase" -> mapping
- "phrase" -> mapping
END_MAPPING

Rules:
- ALWAYS output BEGIN_SQL and END_SQL
- ALWAYS output BEGIN_EXPLANATION and END_EXPLANATION
- ALWAYS output BEGIN_MAPPING and END_MAPPING
- Do not add anything after END_MAPPING
- Each mapping MUST be its own bullet line
"""

    return call_ollama(prompt)

st.title("Explainable NL2SQL (Generic Demo)")
st.write("Enter a question and the model will generate SQL + explanation + mapping")

user_input = st.text_input("Ask a question", placeholder="e.g., show customers older than 30")

if st.button("Generate") and user_input.strip() != "":
    output = generate_sql_and_explanation(user_input)

    if "BEGIN_SQL" in output and "END_SQL" in output:
        sql_block = output.split("BEGIN_SQL")[1].split("END_SQL")[0]
        st.subheader("SQL Query")
        st.code(sql_block.strip(), language="sql")

    if "BEGIN_EXPLANATION" in output and "END_EXPLANATION" in output:
        explanation = output.split("BEGIN_EXPLANATION")[1].split("END_EXPLANATION")[0]
        st.subheader("Explanation")
        st.write(explanation.strip())

    if "BEGIN_MAPPING" in output and "END_MAPPING" in output:
        mapping = output.split("BEGIN_MAPPING")[1].split("END_MAPPING")[0]
        st.subheader("Mappings")
        st.write(mapping.strip())
