import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, Course, Enrollment, Payment, ActivityLog, ChatMessage


@login_required
def dashboard(request):
    # Summary Stats
    total_users = UserProfile.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # Activity Trends (Last 7 Days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # Generate daily trend for all 7 days even if no data
    days = [(timezone.now() - timedelta(days=i)).date() for i in range(6, -1, -1)]
    
    activity_query = (
        ActivityLog.objects.filter(created_at__gte=seven_days_ago)
        .extra(select={'day': "DATE(created_at)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    activity_map = {str(item['day']): item['count'] for item in activity_query}
    activity_trend = [{'day': str(d), 'count': activity_map.get(str(d), 0)} for d in days]

    # Chat Analytics
    most_active_users = list(
        ChatMessage.objects.values('sender__name')
        .annotate(msg_count=Count('id'))
        .order_by('-msg_count')[:5]
    )
    
    chat_query = (
        ChatMessage.objects.filter(created_at__gte=seven_days_ago)
        .extra(select={'day': "DATE(created_at)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    chat_map = {str(item['day']): item['count'] for item in chat_query}
    chat_daily_trend = [{'day': str(d), 'count': chat_map.get(str(d), 0)} for d in days]

    # Top Courses
    top_courses = list(
        Course.objects.annotate(enroll_count=Count('enrollments'))
        .order_by('-enroll_count')[:5]
        .values('title', 'enroll_count')
    )

    # Recent Activity Feed
    recent_activities = ActivityLog.objects.select_related('user').order_by('-created_at')[:10]

    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_revenue': float(total_revenue),
        'activity_trend_json': json.dumps(activity_trend),
        'top_courses_json': json.dumps(top_courses),
        'most_active_chatters_json': json.dumps(most_active_users),
        'chat_daily_trend_json': json.dumps(chat_daily_trend),
        'recent_activities': recent_activities,
    }

    return render(request, 'core/dashboard.html', context)
