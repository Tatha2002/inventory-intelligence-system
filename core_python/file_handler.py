
import pandas as pd


REQUIRED_COLUMNS = ["sku", "product_name", "category", "brand", "warehouse", "stock_quantity", "reorder_level", "purchase_price", "selling_price", "order_count", "return_count", "complaint_text", "supplier_code", "product_image_name", "historical_demand_label"]


def read_inventory_file(file_path):
    file_path = str(file_path)

    if file_path.endswith(".csv"):
        data = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        data = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")

    # Normalize column names
    data.columns = data.columns.str.strip().str.lower()

    # Check required columns
    missing_columns = set(REQUIRED_COLUMNS) - set(data.columns)

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    return data


def display_inventory(data):
    print("\n===== INVENTORY DATA =====")
    print(data)
    print("\nTotal Records:", len(data))
