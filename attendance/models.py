from datetime import date

from django.db import models
from accounts.models import Lecturer


class Course(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    # lecturers = models.ManyToManyField(Lecturer)

    def __str__(self):
        return f"{self.code} - {self.name}"

def get_first_lecturer():
    first_lecturer = Lecturer.objects.first()
    return first_lecturer.id if first_lecturer else None

class ClassSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    program = models.CharField(max_length=100, default="BIT")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, default=get_first_lecturer)
    class_group = models.CharField(max_length=50, null=False, blank=False, default="BIT L400 Group C")
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK, default=DAYS_OF_WEEK[0][0])
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateField(default=date.today)
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.course} - {self.get_day_of_week_display()} - {self.start_time} to {self.end_time} at {self.location}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'class_group', 'day_of_week', 'lecturer'], name='unique_course_group_day')
        ]

class AttendanceRecord(models.Model):
    schedule = models.ForeignKey(ClassSchedule, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    verification_time = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.schedule} - {self.date} - {self.verified}"