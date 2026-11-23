
from pathlib import Path
from core_python.file_handler import read_inventory_file

base_folder = Path(__file__).resolve().parent
input_folder = base_folder / "input"

for file_name in ["sample_inventory.csv", "sample_inventory.xlsx"]:
    print(f"\n===== CHECKING {file_name} =====")

    data = read_inventory_file(input_folder / file_name)

    print("Columns:", list(data.columns))
    print("Total rows:", len(data))
    print("\nFirst 5 records:")
    print(data.head().to_string(index=False))
