import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# =============================
# STEP 1: Load CSV and Fetch HTML Descriptions
# =============================

def load_grants_csv(file_path):
    df = pd.read_csv(file_path)
    return df

def get_grant_description_from_html(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return ""
        soup = BeautifulSoup(response.text, 'html.parser')
        summary = soup.find("div", class_="main") or soup.find("body")
        return summary.get_text(separator=" ", strip=True)#[:5000]   #Limit length
    except Exception as e:
        return ""

# =============================
# STEP 2: Build Corpus
# =============================

def build_opportunity_text(row, description):
    parts = [
        row.get("Title", ""),
        row.get("Activity_Code", ""),
        row.get("Organization", ""),
        row.get("Document_Number", ""),
        row.get("Document_Type", ""),
        row.get("Clinical_Trials", ""),
        description
    ]
    return " | ".join([str(p) for p in parts if pd.notnull(p)])

def build_corpus(df):
    corpus = []
    for _, row in df.iterrows():
        desc = get_grant_description_from_html(row.get("URL", ""))
        text = build_opportunity_text(row, desc)
        corpus.append(text)
    return corpus

# =============================
# STEP 3: Embedding and Search
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

def search_opportunities(user_query, model, index, df, top_k=15):
    query_vec = model.encode([user_query])
    D, I = index.search(np.array(query_vec), k=top_k)
    seen_urls = set()
    unique_rows = []
    for i in I[0]:
        row = df.iloc[i]
        url = row.get("URL")
        if url not in seen_urls:
            seen_urls.add(url)
            unique_rows.append(row)
        if len(unique_rows) == 5:
            break
    return unique_rows

# =============================
# MAIN
# =============================

def main():
    file_path = "NIH_Guide_Results.csv"
    df = load_grants_csv(file_path)

    print("\n🔎 Building semantic search index from NIH opportunities...")
    corpus = build_corpus(df)
    embeddings, model = embed_corpus(corpus)
    index = build_faiss_index(embeddings)

    while True:
        user_query = input("\n💬 Enter your funding need (or 'exit'): ")
        if user_query.lower() in ("exit", "quit"):
            break

        results = search_opportunities(user_query, model, index, df)
        for i, row in enumerate(results):
            print(f"\n{i+1}. Title: {row['Title']}\n   Activity: {row['Activity_Code']} | Org: {row['Organization']}\n   Type: {row['Document_Type']} | Clinical Trials: {row['Clinical_Trials']}\n   URL: {row['URL']}")

if __name__ == "__main__":
    main()
