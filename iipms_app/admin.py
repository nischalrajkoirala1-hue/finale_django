# =============================================================
# admin.py
# Registers all models so they appear in Django's admin panel.
#
# After running the server, visit http://127.0.0.1:8000/admin/
# and log in with the superuser account you created via
# python manage.py createsuperuser
# =============================================================

from django.contrib         import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, StudentProfile, EmployerProfile, SupervisorProfile,
    Internship, Application, WeeklyLog, Offer, Evaluation,
    Notification, ProgressEntry, SupervisorAssignment, Completion,
)


# ── Custom User Admin ─────────────────────────────────────────
# We extend Django's built-in UserAdmin to show our custom fields.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Shows all users in the admin with role and photo columns."""

    # Columns shown in the list view
    list_display  = ("username", "email", "first_name", "last_name", "role", "is_active")
    list_filter   = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")

    # Add our custom fields to the edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        ("IIPMS Fields", {
            "fields": ("role", "photo", "phone"),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("IIPMS Fields", {
            "fields": ("role", "email", "first_name", "last_name"),
        }),
    )


# ── Student Profile ───────────────────────────────────────────

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "course", "wam", "skills", "is_eligible")
    list_filter   = ("is_eligible", "industry_pref", "work_type")
    search_fields = ("user__first_name", "user__last_name", "user__email", "skills")


# ── Employer Profile ──────────────────────────────────────────

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display  = ("company_name", "user", "industry", "verification_status")
    list_filter   = ("verification_status",)
    search_fields = ("company_name", "user__email")
    # Allow the officer to approve verifications directly in admin
    actions       = ["approve_verification", "reject_verification"]

    def approve_verification(self, request, queryset):
        queryset.update(verification_status="Approved")
        self.message_user(request, "Selected employers approved.")
    approve_verification.short_description = "Approve selected employer verifications"

    def reject_verification(self, request, queryset):
        queryset.update(verification_status="Rejected")
        self.message_user(request, "Selected employers rejected.")
    reject_verification.short_description = "Reject selected employer verifications"


# ── Supervisor Profile ────────────────────────────────────────

@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "university", "department")
    search_fields = ("user__first_name", "user__last_name", "university")


# ── Internship ────────────────────────────────────────────────

@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display  = ("title", "company", "location", "is_active", "created_at")
    list_filter   = ("is_active", "industry", "work_type")
    search_fields = ("title", "company", "skills")
    list_editable = ("is_active",)   # toggle active/inactive from the list


# ── Application ───────────────────────────────────────────────

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ("student", "internship", "status", "applied_at")
    list_filter   = ("status",)
    search_fields = ("student__first_name", "student__last_name", "internship__title")
    readonly_fields = ("applied_at",)


# ── Weekly Log ────────────────────────────────────────────────

@admin.register(WeeklyLog)
class WeeklyLogAdmin(admin.ModelAdmin):
    list_display  = ("student", "company_name", "week_number", "hours_worked", "submitted_at")
    search_fields = ("student__first_name", "student__last_name", "company_name")
    readonly_fields = ("submitted_at",)


# ── Offer ─────────────────────────────────────────────────────

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display  = ("student", "internship", "status", "officer_approved", "created_at")
    list_filter   = ("status", "officer_approved")
    search_fields = ("student__first_name", "internship__title")


# ── Evaluation ────────────────────────────────────────────────

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display  = ("student", "evaluator", "internship", "rating_overall", "submitted_at")
    search_fields = ("student__first_name", "evaluator__first_name")


# ── Notification ──────────────────────────────────────────────

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ("recipient", "subject", "from_name", "is_read", "created_at")
    list_filter   = ("is_read",)
    search_fields = ("recipient__email", "subject")
    readonly_fields = ("created_at",)


# ── Progress Entry ────────────────────────────────────────────

@admin.register(ProgressEntry)
class ProgressEntryAdmin(admin.ModelAdmin):
    list_display  = ("student", "internship", "stage", "set_by", "created_at")
    list_filter   = ("stage",)


# ── Supervisor Assignment ─────────────────────────────────────

@admin.register(SupervisorAssignment)
class SupervisorAssignmentAdmin(admin.ModelAdmin):
    list_display  = ("student", "supervisor", "assigned_by", "assigned_at")
    search_fields = ("student__first_name", "supervisor__first_name")


# ── Completion ────────────────────────────────────────────────

@admin.register(Completion)
class CompletionAdmin(admin.ModelAdmin):
    list_display  = ("student", "internship", "completion_date", "recorded_by", "recorded_at")
    search_fields = ("student__first_name", "internship__title")
