from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from .face_training import train_and_save_model
from .models import CustomUser, Lecturer


@admin.action(description="Train and Save Face Model for Selected Users")
def train_models_for_selected_users(modeladmin, request, queryset):
    success_count = 0
    error_count = 0

    for user in queryset:
        try:
            train_and_save_model(user)
            success_count += 1
        except Exception as e:
            error_count += 1
            messages.warning(request, f"User {user.email or user.username}: {str(e)}")

    messages.success(request, f"{success_count} user model(s) trained successfully.")
    if error_count > 0:
        messages.error(request, f"{error_count} model(s) failed. See warnings above.")

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "model_trained", "face_verified")
    list_editable = ('model_trained', "face_verified")
    list_filter = ("is_staff", "is_active", "model_trained", "face_verified")
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")
    actions = [train_models_for_selected_users]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "first_name", "last_name", "is_staff", "is_active"),
        }),
    )





@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'department')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'department')
    list_filter = ('department',)

    def email(self, obj):
        return obj.user.email

    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"