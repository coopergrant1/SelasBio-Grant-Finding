# clean_grant_csv.py

import pandas as pd
import re

# ===============================
# STEP 1: Load and Preview CSV
# ===============================

def load_csv(file_path):
    df = pd.read_csv(file_path, dtype=str, low_memory=False)
    return df

# ===============================
# STEP 2: Clean Grant Data
# ===============================

def clean_grant_data(df):
    # Select relevant columns
    selected_columns = [
        "APPLICATION_ID", "AWARD_NOTICE_DATE", "BUDGET_START", "BUDGET_END",
        "ORG_NAME", "ORG_STATE", "ORG_CITY", "ORG_COUNTRY", "PI_NAMEs",
        "PROJECT_TITLE", "PROJECT_TERMS", "TOTAL_COST", "TOTAL_COST_SUB_PROJECT"
    ]

    # Drop missing project titles
    df = df[selected_columns].dropna(subset=["PROJECT_TITLE"])

    # Standardize column names
    df.columns = [col.lower() for col in df.columns]

    # Clean up project terms (optional: tokenize keywords)
    df["project_terms"] = df["project_terms"].fillna("").apply(lambda x: ", ".join(re.findall(r"\b\w+(?: \w+)?\b", x)))

    # Parse and standardize date fields
    df["award_notice_date"] = pd.to_datetime(df["award_notice_date"], errors="coerce")
    df["budget_start"] = pd.to_datetime(df["budget_start"], errors="coerce")
    df["budget_end"] = pd.to_datetime(df["budget_end"], errors="coerce")

    return df

# ===============================
# STEP 3: Save to Cleaned CSV
# ===============================

def save_cleaned_csv(df, output_path="cleaned_grants.csv"):
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned data saved to {output_path}")

# ===============================
# MAIN
# ===============================

def main():
    input_path = "RePORTER_PRJ_C_FY2024.csv"
    df = load_csv(input_path)
    print("🔍 Loaded:", df.shape)

    cleaned_df = clean_grant_data(df)
    print("✅ Cleaned:", cleaned_df.shape)

    save_cleaned_csv(cleaned_df)


if __name__ == "__main__":
    main()
