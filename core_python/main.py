
from pathlib import Path

from core_python.file_handler import read_inventory_file
from core_python.validators import validate_inventory_row
from core_python.exceptions import InvalidInventoryRow

from core_python.report_generator import (
    generate_cleaned_inventory,
    generate_reorder_alert,
    generate_supplier_issue_report
)


class InventoryAutomation:

    def __init__(self):
        self.base_folder = Path(__file__).resolve().parent
        self.input_folder = self.base_folder / "input"
        self.output_folder = self.base_folder / "output"
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def process_inventory(self, file_name):
        file_path = self.input_folder / file_name
        data = read_inventory_file(file_path)

        valid_records = []
        invalid_records = []

        for row in data.to_dict(orient="records"):
            try:
                valid_records.append(validate_inventory_row(row))
            except InvalidInventoryRow as error:
                invalid_records.append({"row": row, "error": str(error)})

        print(f"\nProcessing: {file_name}")
        print("Valid Records:", len(valid_records))
        print("Invalid Records:", len(invalid_records))

        for record in invalid_records:
            print(record["error"])

        return valid_records

    def run(self):
        print("===== CSV INVENTORY PROCESSING =====")
        csv_records = self.process_inventory("sample_inventory.csv")

        print("\n===== EXCEL INVENTORY PROCESSING =====")
        excel_records = self.process_inventory("sample_inventory.xlsx")

        # Combine valid records from both files
        all_records = csv_records + excel_records

        print("\n===== DEBUG INFORMATION =====")
        print("CSV Valid Records:", len(csv_records))
        print("Excel Valid Records:", len(excel_records))
        print("Total Valid Records:", len(all_records))

        print("\n===== GENERATING INVENTORY REPORTS =====")

        generate_cleaned_inventory(all_records, self.output_folder)
        generate_reorder_alert(all_records, self.output_folder)
        generate_supplier_issue_report(all_records, self.output_folder)

        print("\nAll inventory reports generated successfully!")


if __name__ == "__main__":
    automation = InventoryAutomation()
    automation.run()
