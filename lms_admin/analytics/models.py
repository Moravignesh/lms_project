from django.db import models
from django.utils import timezone
from core.models import UserProfile, Course


class Attendance(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    date = models.DateField()
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'attendance'
        managed = False


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    file_url = models.CharField(max_length=500, blank=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'assignments'
        managed = False


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING)
    student = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING)
    file_url = models.CharField(max_length=500)
    submitted_at = models.DateTimeField(default=timezone.now)
    grade = models.FloatField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'submissions'
        managed = False
