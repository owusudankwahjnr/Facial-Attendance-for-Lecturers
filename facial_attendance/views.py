from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def dashboard(request):

    if request.user.is_superuser:
        return redirect('admin_dashboard')

    if hasattr(request.user, 'lecturer'):
        return redirect('today_schedule')

    if not request.user.face_verified:
        return redirect('verify_face_page')

    return render(request, 'attendance/dashboard.html', {'user': request.user})

