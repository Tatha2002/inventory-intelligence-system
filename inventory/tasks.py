
from celery import shared_task
from django.core.files.storage import default_storage

from inventory.services import import_inventory_csv


@shared_task(bind=True)
def upload_inventory_task(self, file_path):

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 20,
                "message": "Reading inventory CSV file..."
            }
        )

        with default_storage.open(file_path, "rb") as inventory_file:

            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": 50,
                    "message": "Validating and importing inventory..."
                }
            )

            result = import_inventory_csv(inventory_file)

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 90,
                "message": "Generating inventory report..."
            }
        )

        return {
            "status": "COMPLETED",
            "progress": 100,
            "message": "Inventory upload completed successfully.",
            "result": result
        }

    except Exception as error:
        raise error
