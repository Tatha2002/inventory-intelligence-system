
import uuid
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.http import JsonResponse
from celery.result import AsyncResult

from inventory.forms import InventoryUploadForm
from inventory.tasks import upload_inventory_task


def can_upload_inventory(user):
    return user.is_superuser or user.role == "STORE_MANAGER"



@login_required
@user_passes_test(can_upload_inventory)
def upload_inventory(request):

    if request.method == "POST":

        form = InventoryUploadForm(request.POST, request.FILES)

        if form.is_valid():

            uploaded_file = form.cleaned_data["file"]

            try:
                file_path = default_storage.save(
                    f"inventory_uploads/{uuid.uuid4().hex}_{uploaded_file.name}",
                    uploaded_file
                )

                print("FILE PATH:", file_path)
                print("MEDIA ROOT:", settings.MEDIA_ROOT)
                print("FULL PATH:", default_storage.path(file_path))
                print("FILE EXISTS:", default_storage.exists(file_path))

                task = upload_inventory_task.delay(file_path)

                return JsonResponse({
                    "success": True,
                    "task_id": task.id,
                    "file_path": file_path,
                    "message": "Inventory upload started successfully."
                })

            except Exception as error:
                return JsonResponse({
                    "success": False,
                    "message": str(error)
                }, status=500)

        return JsonResponse({
            "success": False,
            "errors": form.errors.get_json_data()
        }, status=400)

    form = InventoryUploadForm()

    return render(request, "inventory/upload_csv.html", {
        "form": form
    })


@login_required
@user_passes_test(can_upload_inventory)
def inventory_task_status(request, task_id):

    task = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task.state
    }

    if task.state == "PROGRESS":

        progress_data = task.info or {}

        response.update({
            "progress": progress_data.get("progress", 0),
            "message": progress_data.get(
                "message",
                "Processing inventory..."
            )
        })

    elif task.state == "SUCCESS":

        result_data = task.result or {}

        response.update({
            "progress": 100,
            "message": result_data.get(
                "message",
                "Inventory upload completed."
            ),
            "result": result_data.get("result", {})
        })

    elif task.state == "FAILURE":

        response.update({
            "message": "Inventory upload failed.",
            "error": str(task.info)
        })

    return JsonResponse(response)
