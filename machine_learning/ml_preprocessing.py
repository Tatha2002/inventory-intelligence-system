
import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "inventory_dataset.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "cleaned_inventory.csv")
VISUALIZATION_DIR = os.path.join(BASE_DIR, "visualizations")

TARGET = "historical_demand_label"
NUMERIC_FEATURES = ["stock_quantity", "reorder_level", "order_count", "return_count", "selling_price"]
CATEGORICAL_FEATURES = ["category", "brand", "warehouse", "supplier_code"]
SELECTED_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

def load_dataset():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print("Dataset loaded successfully.")
    print("Original shape:", df.shape)
    return df

def clean_dataset(df):
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df = df.drop_duplicates()
    required_columns = SELECTED_FEATURES + [TARGET]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    df = df[required_columns].copy()
    for column in NUMERIC_FEATURES:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        df[column] = df[column].fillna(df[column].median())
    for column in CATEGORICAL_FEATURES:
        df[column] = df[column].fillna("Unknown").astype(str).str.strip()
    df[TARGET] = df[TARGET].astype(str).str.strip().str.title()
    df = df[df[TARGET].isin(["High", "Medium", "Low"])]
    for column in NUMERIC_FEATURES:
        lower = df[column].quantile(0.25)
        upper = df[column].quantile(0.75)
        iqr = upper - lower
        if iqr > 0:
            df[column] = df[column].clip(lower - 1.5 * iqr, upper + 1.5 * iqr)
    return df.dropna(subset=[TARGET]).reset_index(drop=True)

def generate_visualizations(df):
    os.makedirs(VISUALIZATION_DIR, exist_ok=True)
    plt.figure(figsize=(7, 5))
    df[TARGET].value_counts().reindex(["High", "Medium", "Low"], fill_value=0).plot(kind="bar")
    plt.title("Historical Demand Distribution")
    plt.xlabel("Demand Label")
    plt.ylabel("Product Count")
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, "demand_distribution.png"))
    plt.close()
    df[NUMERIC_FEATURES].hist(figsize=(10, 8))
    plt.suptitle("Inventory Feature Distributions")
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, "feature_distributions.png"))
    plt.close()

def preprocess_dataset():
    df = load_dataset()
    cleaned_df = clean_dataset(df)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    cleaned_df.to_csv(OUTPUT_PATH, index=False)
    generate_visualizations(cleaned_df)
    print("Preprocessing completed successfully.")
    print("Cleaned dataset shape:", cleaned_df.shape)
    print("Demand distribution:")
    print(cleaned_df[TARGET].value_counts())
    return cleaned_df

if __name__ == "__main__":
    preprocess_dataset()
