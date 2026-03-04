from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.views.decorators.http import require_GET
from core.models import Enrollment
from .models import Attendance, Assignment, Submission


@require_GET
def dashboard(request):
    course_id = request.GET.get("course_id")
    if not course_id:
        return JsonResponse({"error": "course_id required"}, status=400)
    total_students = Enrollment.objects.filter(course_id=course_id).count()
    total_assignments = Assignment.objects.filter(course_id=course_id).count()
    submissions_count = Submission.objects.filter(assignment__course_id=course_id).count()
    qs = Attendance.objects.filter(course_id=course_id)
    total = qs.count()
    present = qs.filter(status__iexact="present").count()
    avg_attendance = round((present / total * 100.0), 2) if total > 0 else 0.0
    data = {
        "course_id": int(course_id),
        "total_students": total_students,
        "avg_attendance": avg_attendance,
        "total_assignments": total_assignments,
        "submissions_count": submissions_count,
    }
    return JsonResponse(data)
