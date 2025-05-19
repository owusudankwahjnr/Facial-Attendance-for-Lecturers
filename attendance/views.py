import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from attendance.models import ClassSchedule, AttendanceRecord, Course
from accounts.models import Lecturer
from django.db.models import Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
current_time = now().time()
import datetime

def is_admin_user(user):
    return user.is_superuser


from django.utils import timezone
from datetime import timedelta
from collections import defaultdict


def get_attendance_summary():
    today = timezone.now().date()
    results = []

    for schedule in ClassSchedule.objects.select_related('course').prefetch_related('course__lecturers'):
        # 1. Calculate number of expected sessions
        day_code = schedule.day_of_week  # e.g. "MON"
        day_index = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'].index(day_code)

        # Assume schedule has been active since creation of the ClassSchedule object
        # If no `created_at`, fallback to earliest AttendanceRecord or skip
        earliest_record = AttendanceRecord.objects.filter(schedule=schedule).order_by('timestamp').first()
        schedule_start_date = earliest_record.timestamp.date() if earliest_record else schedule.date if hasattr(
            schedule, 'date') else today - timedelta(weeks=5)

        expected_count = 0
        current = schedule_start_date
        while current <= today:
            if current.weekday() == day_index:
                expected_count += 1
            current += timedelta(days=1)

        # 2. Get actual attendance records marked as verified
        actual_count = AttendanceRecord.objects.filter(schedule=schedule, verified=True).count()

        # 3. Format lecturers
        lecturers = ", ".join(lec.full_name for lec in schedule.course.lecturers.all())

        results.append({
            'lecturer': lecturers,
            'program': schedule.program,
            'course': f"{schedule.course.code} - {schedule.course.name}",
            'class_group': schedule.class_group,
            'attendance': f"{actual_count} / {expected_count}"
        })

    return results




@login_required
@user_passes_test(is_admin_user)
def admin_dashboard_view(request):
    # Get filter values from query params
    lecturer_id = request.GET.get("lecturer_id")
    program = request.GET.get("program")
    course_id = request.GET.get("course_id")
    class_group = request.GET.get("class_group")

    # Base queryset
    schedules = ClassSchedule.objects.select_related('course', 'lecturer').prefetch_related('attendancerecord_set')

    # Apply filters
    if lecturer_id:
        schedules = schedules.filter(lecturer_id=lecturer_id)
    if program:
        schedules = schedules.filter(program=program)
    if course_id:
        schedules = schedules.filter(course_id=course_id)
    if class_group:
        schedules = schedules.filter(class_group=class_group)

    # Generate rows
    rows = []
    for schedule in schedules:
        first_attendance = schedule.attendancerecord_set.order_by('date').first()
        start_date = first_attendance.date if first_attendance else schedule.created_at
        weeks_since_start = max(1, ((datetime.date.today() - start_date).days // 7))
        verified_count = schedule.attendancerecord_set.filter(verified=True).count()

        lecturer = schedule.lecturer
        rows.append({
            "lecturer": f"{lecturer.user.first_name} {lecturer.user.last_name}",
            "email": lecturer.user.email,
            "program": schedule.program,
            "course": f"{schedule.course.code} - {schedule.course.name}",
            "class_group": schedule.class_group,
            "attendance": f"{verified_count} / {weeks_since_start}",
        })

    # ✅ If export is requested, return CSV response
    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=attendance_report.csv"
        writer = csv.writer(response)
        writer.writerow(["Lecturer", "Email", "Program", "Course", "Class Group", "Attendance (Verified / Total)"])
        for row in rows:
            writer.writerow([
                row["lecturer"],
                row["email"],
                row["program"],
                row["course"],
                row["class_group"],
                row["attendance"]
            ])
        return response

    # For dropdown filters
    lecturers = Lecturer.objects.all()
    programs = ClassSchedule.objects.values_list("program", flat=True).distinct()
    courses = Course.objects.all()
    class_groups = ClassSchedule.objects.values_list("class_group", flat=True).distinct()

    context = {
        'total_lecturers': Lecturer.objects.count(),
        'total_courses': Course.objects.count(),
        'total_schedules': ClassSchedule.objects.count(),
        'total_attendance': AttendanceRecord.objects.count(),
        'attendance_rows': rows,

        # For filters
        'lecturers': lecturers,
        'programs': programs,
        'courses': courses,
        'class_groups': class_groups,
    }

    return render(request, 'attendance/admin_dashboard.html', context)




@login_required
def today_schedule_view(request):
    user = request.user

    if not user.face_verified:
        return redirect('verify_face_page')

    try:
        lecturer = Lecturer.objects.get(user=user)
    except Lecturer.DoesNotExist:
        return redirect('unauthorized')

    day_code = now().strftime('%a').upper()[:3]
    # courses = Course.objects.filter(lecturers=lecturer)

    schedules = ClassSchedule.objects.filter(
        day_of_week=day_code,
        lecturer=lecturer
    ).annotate(attendance_count=Count('attendancerecord'))

    current_time = now().time()
    for schedule in schedules:
        schedule.is_current = schedule.start_time <= current_time <= schedule.end_time

    return render(request, 'attendance/today_schedule.html', {'schedules': schedules})


@login_required
def verify_attendance(request, schedule_id):
    user = request.user

    # Ensure face verification
    if not user.face_verified:
        return redirect('verify_face_page')

    schedule = get_object_or_404(ClassSchedule, id=schedule_id)

    try:
        lecturer = Lecturer.objects.get(user=user)
    except Lecturer.DoesNotExist:
        return redirect('unauthorized')

    # Check that the lecturer is allowed to mark attendance for this course
    if lecturer != schedule.lecturer:
        return redirect('unauthorized')

    # Prevent duplicate records for the same day & schedule
    today = now().date()
    record = AttendanceRecord.objects.filter(schedule=schedule, date=today).first()


    if not record:
        AttendanceRecord.objects.create(
            schedule=schedule,
            verified=True,
            verification_time=now()
        )
        messages.success(request, "Attendance Submitted Successfully.")

    if record:
        messages.warning(request, "Attendance taken already.")
    else:
        messages.error(request, "There was an error taking your attendance.")

    return redirect('today_schedule')



@login_required
def all_schedules_view(request):
    user = request.user

    try:
        lecturer = Lecturer.objects.get(user=user)
    except Lecturer.DoesNotExist:
        return redirect('unauthorized')

    # courses = Course.objects.filter(lecturer=lecturer)
    schedules = ClassSchedule.objects.filter(lecturer=lecturer)

    # Filters
    selected_day = request.GET.get('day')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    search_query = request.GET.get('search')
    selected_program = request.GET.get('program')

    if selected_day:
        schedules = schedules.filter(day_of_week=selected_day)

    if start_time:
        schedules = schedules.filter(start_time__gte=start_time)

    if end_time:
        schedules = schedules.filter(end_time__lte=end_time)

    if search_query:
        schedules = schedules.filter(
            Q(course__name__icontains=search_query) |
            Q(course__code__icontains=search_query)
        )

    if selected_program:
        schedules = schedules.filter(program=selected_program)

    # Get distinct programs from ClassSchedule for the filter dropdown
    programs = ClassSchedule.objects.values_list('program', flat=True).distinct()

    # Pagination
    paginator = Paginator(schedules.order_by('day_of_week', 'start_time'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'selected_day': selected_day,
        'start_time': start_time,
        'end_time': end_time,
        'search_query': search_query,
        'selected_program': selected_program,
        'programs': programs,
        'days': ClassSchedule.DAYS_OF_WEEK,
    }

    return render(request, 'attendance/all_schedules.html', context)

