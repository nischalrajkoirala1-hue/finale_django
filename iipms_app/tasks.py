# =============================================================
# tasks.py
# Celery background tasks — these run automatically on a schedule
# without a user triggering them.
#
# HOW TO RUN:
# 1. Install: pip install celery redis
# 2. Start Redis:   redis-server
# 3. Start worker:  celery -A iipms_project worker -l info
# 4. Start beat:    celery -A iipms_project beat -l info
#
# The CELERYBEAT_SCHEDULE in settings.py (or here) controls
# how often each task runs.
# =============================================================

from celery           import shared_task
from django.utils     import timezone
from django.core.mail import send_mail
from django.conf      import settings
import datetime


@shared_task
def remind_students_to_submit_log():
    """
    Runs every Monday morning.
    Sends a reminder to every student who has a hired application
    but has not submitted a log this week.
    """
    # Import here to avoid circular imports
    from iipms_app.models import User, Application, WeeklyLog, Notification

    # Find the start of the current week (Monday)
    today          = timezone.now().date()
    week_start     = today - datetime.timedelta(days=today.weekday())

    # Get all students who have been hired somewhere
    hired_apps = Application.objects.filter(
        status=Application.STATUS_HIRED
    ).select_related("student")

    for app in hired_apps:
        student = app.student

        # Check if they submitted a log this week
        submitted_this_week = WeeklyLog.objects.filter(
            student      = student,
            submitted_at__gte = timezone.make_aware(
                datetime.datetime.combine(week_start, datetime.time.min)
            ),
        ).exists()

        if not submitted_this_week:
            # Create an in-app notification
            Notification.objects.create(
                recipient = student,
                from_name = "IIPMS Placement System",
                subject   = "⏰ Weekly Log Reminder",
                message   = (
                    f"Hi {student.first_name}, don't forget to submit your "
                    "weekly progress log for this week! Log in to your "
                    "Student Portal to complete it."
                ),
            )

            # Also send an email if configured
            try:
                send_mail(
                    subject      = "[IIPMS] Weekly Log Reminder",
                    message      = (
                        f"Hi {student.first_name},\n\n"
                        "This is a friendly reminder to submit your weekly progress "
                        "log for the current week.\n\n"
                        "Please log in to your Student Portal to complete it.\n\n"
                        "IIPMS Placement Team"
                    ),
                    from_email   = settings.DEFAULT_FROM_EMAIL,
                    recipient_list = [student.email],
                    fail_silently = True,
                )
            except Exception:
                pass


@shared_task
def auto_close_expired_listings():
    """
    Runs daily.
    Marks internship listings as inactive if their end date has passed.
    (Only works for listings with a properly formatted end_date field.)
    """
    from iipms_app.models import Internship
    import re

    today = timezone.now().date()

    for job in Internship.objects.filter(is_active=True):
        # Try to parse common date formats from the end_date text field
        # e.g. "30 June 2026", "30/06/2026", "2026-06-30"
        date_text = job.end_date.strip()
        parsed    = None

        for fmt in ("%d %B %Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                parsed = datetime.datetime.strptime(date_text, fmt).date()
                break
            except ValueError:
                continue

        if parsed and parsed < today:
            job.is_active = False
            job.save()


@shared_task
def remind_officers_of_pending_verifications():
    """
    Runs every weekday.
    Alerts officers when employer verifications have been waiting more than 2 days.
    """
    from iipms_app.models import User, EmployerProfile, Notification

    two_days_ago = timezone.now() - datetime.timedelta(days=2)

    # Employers who signed up more than 2 days ago and are still pending
    pending_long = EmployerProfile.objects.filter(
        verification_status = "Pending",
        user__date_joined__lte = two_days_ago,
    )

    if pending_long.exists():
        officers = User.objects.filter(role=User.ROLE_OFFICER)
        count    = pending_long.count()

        for officer in officers:
            Notification.objects.create(
                recipient = officer,
                from_name = "IIPMS System",
                subject   = f"⚠️ {count} Employer Verification(s) Pending Review",
                message   = (
                    f"There are {count} employer verification request(s) that have been "
                    "waiting for more than 2 days. Please review them in the Officer Dashboard."
                ),
            )


@shared_task
def remind_supervisors_to_submit_evaluations():
    """
    Runs monthly.
    Reminds supervisors who have assigned students but no evaluations submitted yet.
    """
    from iipms_app.models import SupervisorAssignment, Evaluation, Notification

    # Find assignments with no evaluation submitted by that supervisor
    assignments = SupervisorAssignment.objects.select_related("supervisor", "student").all()

    for assignment in assignments:
        has_eval = Evaluation.objects.filter(
            evaluator  = assignment.supervisor,
            student    = assignment.student,
        ).exists()

        if not has_eval:
            Notification.objects.create(
                recipient = assignment.supervisor,
                from_name = "IIPMS Placement System",
                subject   = f"📋 Evaluation Reminder — {assignment.student.get_full_name()}",
                message   = (
                    f"You have not yet submitted an evaluation for "
                    f"{assignment.student.get_full_name()}. "
                    "Please log in to your Supervisor Portal to complete the evaluation."
                ),
            )
