# grant_llm_agent.py

import requests
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import tool

# ===============
# TOOL DEFINITION
# ===============

@tool
def search_grants(keyword: str, eligibility: str = "99", max_results: int = 3) -> str:
    """Searches grants.gov for grant opportunities by keyword and eligibility."""
    url = "https://api.grants.gov/v2/opportunities/search"
    headers = {"api_key": "YOUR_GRANTS_GOV_API_KEY"}  # <- REPLACE THIS
    params = {
        "keyword": keyword,
        "eligibilityCodes": eligibility,
        "limit": max_results
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return f"API error: {response.status_code} - {response.text}"

    opportunities = response.json().get("opportunities", [])
    if not opportunities:
        return "No matching grant opportunities found."

    # Return top N results, formatted cleanly
    result = []
    for opp in opportunities:
        entry = f"""
        🔹 Title: {opp.get('title')}
        🔹 Agency: {opp.get('agencyCode')}
        🔹 CFDA: {opp.get('cfdaNumber')}
        🔹 Deadline: {opp.get('closeDate')}
        🔹 Summary: {opp.get('synopsis')[:300]}...
        """
        result.append(entry)

    return "\n".join(result)


# ======================
# LLM + AGENT INITIALIZE
# ======================

def main():
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    agent = initialize_agent(
        tools=[search_grants],
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )

    print("\n🔎 Ask your grant-finding assistant anything!\n")
    while True:
        query = input("You: ")
        if query.lower() in ("exit", "quit"): break
        response = agent.run(query)
        print(f"\n🤖 Assistant:\n{response}\n")


if __name__ == "__main__":
    main()
