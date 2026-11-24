import pandas as pd


def generate_cleaned_inventory(records, output_folder):
    data = pd.DataFrame(records)
    file_path = output_folder / "cleaned_inventory.csv"
    data.to_csv(file_path, index=False)
    print(f"Generated: {file_path}")


def generate_reorder_alert(records, output_folder):
    reorder_records = [row for row in records if row["stock_quantity"] <= row["reorder_level"]]
    data = pd.DataFrame(reorder_records)
    file_path = output_folder / "reorder_alert.csv"
    data.to_csv(file_path, index=False)
    print(f"Generated: {file_path}")


def generate_supplier_issue_report(records, output_folder):
    supplier_records = [row for row in records if str(row.get("complaint_text", "")).strip() not in ("", "nan", "None") or row["return_count"] > 0]
    data = pd.DataFrame(supplier_records)
    file_path = output_folder / "supplier_issue_report.csv"
    data.to_csv(file_path, index=False)
    print(f"Generated: {file_path}")
