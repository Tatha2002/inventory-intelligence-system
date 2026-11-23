
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import JsonResponse
from celery.result import AsyncResult
from inventory.models import Complaint
from .models import ComplaintAnalysis
from .tasks import analyze_complaints_task


def is_manager(user):
    return user.is_superuser or getattr(user, "role", None) == "STORE_MANAGER"


@login_required(login_url="portal-login")
@user_passes_test(is_manager)
def complaint_analysis_view(request):
    if request.method == "POST":
        try:
            task = analyze_complaints_task.delay()
            return JsonResponse({"success": True, "task_id": task.id, "message": "Complaint analysis started successfully."})
        except Exception:
            return JsonResponse({"success": False, "message": "Unable to start NLP analysis. Please try again."}, status=500)

    complaints = Complaint.objects.select_related("product").order_by("-created_at")
    analyses = ComplaintAnalysis.objects.select_related("complaint", "complaint__product").all()
    analysis_map = {analysis.complaint_id: analysis for analysis in analyses}

    complaint_data = [{"complaint": complaint, "analysis": analysis_map.get(complaint.id)} for complaint in complaints]

    return render(request, "nlp/complaint_analysis.html", {"complaint_data": complaint_data, "total_complaints": complaints.count(), "analyzed_count": len(analysis_map)})


@login_required(login_url="portal-login")
@user_passes_test(is_manager)
def complaint_analysis_task_status(request, task_id):
    task = AsyncResult(task_id)
    response = {"task_id": task_id, "status": task.state}

    if task.state == "PROGRESS":
        response.update(task.info)
    elif task.state == "SUCCESS":
        response.update({"message": task.result.get("message"), "progress": 100, "count": task.result.get("count")})
    elif task.state == "FAILURE":
        response.update({"message": "NLP complaint analysis failed. Please check the server logs."})

    return JsonResponse(response)
