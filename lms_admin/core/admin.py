from django.contrib import admin
from .models import UserProfile, Course, Lesson, Enrollment, Progress, Plan, Subscription, Payment, CourseMeta, Notification, ActivityLog, ChatRoom, ChatMessage, UserStatus, SocialAccount, OTPLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role')
    search_fields = ('name', 'email')
    list_filter = ('role',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'status')
    list_filter = ('status',)
    search_fields = ('title',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    search_fields = ('title',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_on')
    list_filter = ('enrolled_on',)
    search_fields = ('user__name', 'course__title')


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'completed_lessons', 'progress_percent')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days')
    search_fields = ('name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'status')
    list_filter = ('status',)
    search_fields = ('user__name', 'plan__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'payment_date')
    list_filter = ('payment_date',)
    search_fields = ('user__name', 'plan__name')


@admin.register(CourseMeta)
class CourseMetaAdmin(admin.ModelAdmin):
    list_display = ('course', 'is_premium', 'price')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__name', 'message')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'created_at')
    list_filter = ('action_type',)
    search_fields = ('user__name', 'action_type', 'action_detail')


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_group', 'created_at')
    list_filter = ('is_group',)
    filter_horizontal = ('members',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'room', 'created_at')
    search_fields = ('message', 'sender__name')
    list_filter = ('created_at',)


@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_online', 'last_seen')
    list_filter = ('is_online',)


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'provider_user_id', 'created_at')
    list_filter = ('provider',)
    search_fields = ('user__name', 'provider_user_id')


@admin.register(OTPLog)
class OTPLogAdmin(admin.ModelAdmin):
    list_display = ('email', 'purpose', 'code', 'is_used', 'created_at', 'expires_at')
    list_filter = ('purpose', 'is_used')
    search_fields = ('email', 'code')
