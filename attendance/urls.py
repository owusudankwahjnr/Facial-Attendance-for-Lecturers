from django.urls import path
from . import views
from .views import today_schedule_view, verify_attendance, all_schedules_view, admin_dashboard_view

urlpatterns = [
    path('today-schedule/', today_schedule_view, name='today_schedule'),
    path('verify/<int:schedule_id>/', verify_attendance, name='verify_attendance'),
    path('all-schedules/', all_schedules_view, name='all_schedules'),
    path('admin/dashboard/', admin_dashboard_view, name='admin_dashboard'),
]
