from langchain_openai import ChatOpenAI
import matplotlib.pyplot as plt
import json
import os

def generate_viz_plan(df, question):
    llm = ChatOpenAI(
        model="meta/llama-3.3-70b-instruct",
        openai_api_key=os.getenv("NVIDIA_API_KEY"),
        openai_api_base="https://integrate.api.nvidia.com/v1",
        temperature=0
    )

    columns = list(df.columns)

    prompt = f"""
Columns: {columns}
Question: {question}

Return JSON:
{{
 "chart": "bar/line/scatter",
 "x": "column",
 "y": "column"
}}
"""

    response = llm.invoke(prompt)

    try:
        return json.loads(response.content)
    except:
        return None


def create_chart(df, plan):
    if not plan:
        return None

    chart = plan.get("chart")
    x = plan.get("x")
    y = plan.get("y")

    if x not in df.columns or y not in df.columns:
        return None

    fig, ax = plt.subplots()

    if chart == "bar":
        ax.bar(df[x], df[y])
    elif chart == "line":
        ax.plot(df[x], df[y])
    elif chart == "scatter":
        ax.scatter(df[x], df[y])
    else:
        return None

    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig
