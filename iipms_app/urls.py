# =============================================================
# urls.py  (iipms_app)
# This file maps URL paths to view functions.
#
# HOW URLS WORK:
# - A user visits a URL like /student/dashboard/
# - Django looks through this list top-to-bottom
# - When it finds a match, it calls the linked view function
# - The <int:pk> parts capture numbers from the URL
# =============================================================

from django.urls import path
from . import views

urlpatterns = [

    # ── PUBLIC PAGES ──────────────────────────────────────────
    path("",           views.home,  name="home"),
    path("about/",     views.about, name="about"),

    # ── AUTHENTICATION ────────────────────────────────────────
    path("register/",  views.register_view, name="register"),
    path("login/",     views.login_view,    name="login"),
    path("logout/",    views.logout_view,   name="logout"),

    # ── STUDENT PORTAL ────────────────────────────────────────
    path("student/",
         views.student_dashboard,   name="student_dashboard"),

    path("student/profile/edit/",
         views.student_profile_edit, name="student_profile_edit"),

    path("student/internships/",
         views.internship_list,      name="internship_list"),

    path("student/matches/",
         views.matches_view,         name="matches"),

    path("student/apply/<int:internship_id>/",
         views.apply_view,           name="apply"),

    path("student/withdraw/<int:app_id>/",
         views.withdraw_application, name="withdraw_application"),

    path("student/respond/app/<int:app_id>/",
         views.respond_to_application, name="respond_to_application"),

    path("student/respond/offer/<int:offer_id>/",
         views.respond_to_offer,     name="respond_to_offer"),

    path("student/log/",
         views.weekly_log_view,      name="weekly_log"),

    # Notifications
    path("notifications/read/<int:notif_id>/",
         views.mark_notification_read,      name="mark_notification_read"),
    path("notifications/read-all/",
         views.mark_all_notifications_read, name="mark_all_notifications_read"),
    path("notifications/delete/<int:notif_id>/",
         views.delete_notification,         name="delete_notification"),

    # ── EMPLOYER PORTAL ───────────────────────────────────────
    path("employer/",
         views.employer_dashboard,          name="employer_dashboard"),

    path("employer/post/",
         views.post_internship,             name="post_internship"),

    path("employer/application/<int:app_id>/status/",
         views.update_application_status,   name="update_application_status"),

    path("employer/offer/<int:app_id>/",
         views.issue_offer,                 name="issue_offer"),

    path("employer/evaluate/<int:student_id>/<int:internship_id>/",
         views.submit_evaluation,           name="submit_evaluation"),

    # ── OFFICER DASHBOARD ─────────────────────────────────────
    path("officer/",
         views.officer_dashboard,           name="officer_dashboard"),

    path("officer/verify/<int:profile_id>/",
         views.officer_verify_employer,     name="officer_verify_employer"),

    path("officer/nextstep/<int:app_id>/",
         views.officer_set_next_step,       name="officer_set_next_step"),

    path("officer/offer/<int:offer_id>/",
         views.officer_approve_offer,       name="officer_approve_offer"),

    path("officer/progress/add/",
         views.officer_add_progress,        name="officer_add_progress"),

    path("officer/assign/",
         views.officer_assign_supervisor,   name="officer_assign_supervisor"),

    path("officer/complete/",
         views.officer_mark_complete,       name="officer_mark_complete"),

    # ── SUPERVISOR PORTAL ─────────────────────────────────────
    path("supervisor/",
         views.supervisor_dashboard,        name="supervisor_dashboard"),

    path("supervisor/evaluate/<int:student_id>/<int:internship_id>/",
         views.submit_evaluation,           name="supervisor_evaluate"),

    # ── REPORTS ───────────────────────────────────────────────
    path("reports/",
         views.reports_view,                name="reports"),

    path("reports/export/",
         views.export_csv,                  name="export_csv"),

    # ── JSON API (called from JavaScript) ────────────────────
    path("api/internships/",
         views.api_internships,             name="api_internships"),

    path("api/notifications/",
         views.api_notifications,           name="api_notifications"),
]
