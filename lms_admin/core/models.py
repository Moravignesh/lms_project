from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    password_hash = models.CharField(max_length=255)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.name} ({self.role})'


class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='courses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)

    class Meta:
        db_table = 'lessons'

    def __str__(self):
        return f'{self.course.title}: {self.title}'


class Enrollment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_on = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'enrollments'
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user.name} -> {self.course.title}'


class Progress(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='progress')
    completed_lessons = models.IntegerField(default=0)
    progress_percent = models.FloatField(default=0.0)

    class Meta:
        db_table = 'progress'

    def __str__(self):
        return f'{self.enrollment.user.name} - {self.enrollment.course.title}: {self.progress_percent}%'


class Plan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()

    class Meta:
        db_table = 'plans'

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'subscriptions'

    def __str__(self):
        return f'{self.user.name} - {self.plan.name} ({self.status})'


class Payment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f'{self.user.name} - {self.amount}'


class CourseMeta(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='meta')
    is_premium = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'course_meta'

    def __str__(self):
        return f'{self.course.title} premium={self.is_premium}'


class Notification(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'

    def __str__(self):
        return f'Notif({self.user.name}): {self.message[:20]}...'


class ActivityLog(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='activity_logs')
    action_type = models.CharField(max_length=50)
    action_detail = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'activity_logs'
        indexes = [models.Index(fields=['user', 'created_at'])]

    def __str__(self):
        return f'{self.user.name} - {self.action_type}'


class ChatRoom(models.Model):
    name = models.CharField(max_length=200, blank=True)
    is_group = models.BooleanField(default=False)
    members = models.ManyToManyField(UserProfile, related_name='chat_rooms')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'chat_rooms'

    def __str__(self):
        return self.name or f"Room {self.id}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField(blank=True)
    file_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'chat_messages'
        indexes = [models.Index(fields=['room', 'created_at'])]

    def __str__(self):
        return f'{self.sender.name}: {self.message[:20]}'


class UserStatus(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='status')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'user_status'

    def __str__(self):
        return f'{self.user.name} - {"Online" if self.is_online else "Offline"}'
