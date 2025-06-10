import requests
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# =============================
# STEP 1: Query Grants.gov API
# =============================

def fetch_grantsgov_projects(query_text):
    url = "https://api.grants.gov/v1/api/search2"
    payload = {
        "keyword": query_text,
        # "rows": limit,
        "oppStatuses": "forecasted|posted"
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Grants.gov API error: {response.status_code} - {response.text}")
    return response.json().get("data", {}).get("oppHits", [])

# =============================
# STEP 2: Build Text Corpus
# =============================

def build_project_text(project):
    title = project.get("title", "")
    agency = project.get("agencyCode", "")
    synopsis = project.get("synopsis", "")
    open_date = project.get("openDate", "")
    close_date = project.get("closeDate", "")
    return f"{title} | Agency: {agency} | Synopsis: {synopsis} | Open: {open_date} | Close: {close_date}"

def build_corpus(projects):
    return [build_project_text(p) for p in projects]

# =============================
# STEP 3: Embed and Index
# =============================

def embed_corpus(corpus, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(corpus, show_progress_bar=True, batch_size=64)
    return embeddings, model

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index

# =============================
# STEP 4: Query and Search
# =============================

def search_projects(user_query, model, index, projects, top_k=15):
    q_vec = model.encode([user_query])
    D, I = index.search(np.array(q_vec), k=top_k)
    seen_ids, unique = set(), []
    for i in I[0]:
        proj = projects[i]
        opp_id = proj.get("id")
        if opp_id not in seen_ids:
            seen_ids.add(opp_id)
            unique.append(proj)
            if len(unique) == 5:
                break
    return unique

# =============================
# MAIN
# =============================

def main():
    api_query = input("Enter a topic to search Grants.gov: ")
    print("\n📡 Fetching open opportunities...")
    projects = fetch_grantsgov_projects(api_query)
    if not projects:
        print("No opportunities found.")
        return
    print(f"✅ Retrieved {len(projects)} entries.")

    corpus = build_corpus(projects)
    embeddings, model = embed_corpus(corpus)
    index = build_faiss_index(embeddings)

    while True:
        user_query = input("\n🔎 Describe your funding need (or 'exit'): ")
        if user_query.lower() in ("exit", "quit"):
            break

        results = search_projects(user_query, model, index, projects)
        for i, proj in enumerate(results, 1):
            synopsis = proj.get("synopsis") or "No summary provided."
            print(
                f"\n{i}. Title: {proj.get('title')}\n"
                f"   Opportunity ID: {proj.get('opportunityId')}\n"
                f"   Agency: {proj.get('agencyCode')} | Status: {proj.get('oppStatus')}\n"
                f"   Open: {proj.get('openDate')} — Close: {proj.get('closeDate')}\n"
                f"   Summary: {synopsis[:300]}..."
            )

if __name__ == "__main__":
    main()
