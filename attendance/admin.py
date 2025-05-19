from django.contrib import admin
from .models import Course, ClassSchedule, AttendanceRecord
from accounts.models import Lecturer

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    # filter_horizontal = ('lecturers',)  # Better UI for many-to-many field

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'lecturer', 'class_group', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('course', 'lecturer', 'day_of_week')
    search_fields = ('course__name', 'course__code', 'class_group', 'location')

    def get_lecturers(self, obj):
        return ", ".join([lecturer.user.email for lecturer in obj.course.lecturers.all()])
    get_lecturers.short_description = 'Lecturers'

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'date', 'verified', 'verification_time', 'timestamp')
    list_filter = ('verified', 'date')
    search_fields = ('schedule__course__name', 'schedule__lecturer__user__email')
    autocomplete_fields = ('schedule',)
