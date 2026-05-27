# =============================================================
# views.py
# Every page and action in the IIPMS system is a function here.
#
# HOW VIEWS WORK:
# - Django calls the right function when a URL is visited.
# - The function reads the database, decides what to show,
#   and returns an HTML page (render) or a redirect.
# - @login_required means: if not logged in, go to login page.
# - We use helper functions (require_role) to restrict pages
#   to the correct user type.
# =============================================================

from django.shortcuts          import render, redirect, get_object_or_404
from django.contrib.auth       import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib            import messages
from django.http               import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils              import timezone
from django.db.models          import Count, Q
from django.core.mail          import send_mail
from django.conf               import settings

import csv
import json

from .models   import (
    User, StudentProfile, EmployerProfile, SupervisorProfile,
    Internship, Application, WeeklyLog, Offer, Evaluation,
    Notification, ProgressEntry, SupervisorAssignment, Completion,
)
from .matching  import rank_internships_for_student
from .forms     import (
    RegisterForm, StudentProfileForm, EmployerProfileForm,
    InternshipForm, WeeklyLogForm, EvaluationForm, OfferForm,
)


# =============================================================
# HELPER FUNCTIONS
# Small utilities used throughout this file.
# =============================================================

def require_role(request, *roles):
    """
    Check the logged-in user has one of the given roles.
    If not, redirect them to their own dashboard.
    Returns True if OK, False if we already redirected.
    """
    if request.user.role not in roles:
        messages.error(request, "You do not have permission to view that page.")
        return False
    return True


def send_notification(recipient, from_name, subject, message):
    """
    Save an in-app notification to the database.
    Also attempt to send a real email if Django email is configured.
    """
    Notification.objects.create(
        recipient  = recipient,
        from_name  = from_name,
        subject    = subject,
        message    = message,
    )

    # Try to send a real email too (optional — works if EMAIL settings are configured)
    try:
        send_mail(
            subject      = f"[IIPMS] {subject}",
            message      = message,
            from_email   = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [recipient.email],
            fail_silently = True,    # don't crash the site if email fails
        )
    except Exception:
        pass


# =============================================================
# PUBLIC PAGES (no login required)
# =============================================================

def home(request):
    """
    The public landing page.
    If already logged in, redirect to the right dashboard.
    """
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    return render(request, "iipms_app/index.html")


def about(request):
    """The public About page."""
    return render(request, "iipms_app/about.html")


def redirect_to_dashboard(user):
    """
    Return a redirect to the correct dashboard based on role.
    Used after login and registration.
    """
    role_to_url = {
        User.ROLE_STUDENT:    "student_dashboard",
        User.ROLE_EMPLOYER:   "employer_dashboard",
        User.ROLE_OFFICER:    "officer_dashboard",
        User.ROLE_SUPERVISOR: "supervisor_dashboard",
    }
    url_name = role_to_url.get(user.role, "home")
    return redirect(url_name)


# =============================================================
# AUTHENTICATION: REGISTER, LOGIN, LOGOUT
# =============================================================

def register_view(request):
    """
    GET:  Show the registration form.
    POST: Save the new user and redirect to their dashboard.
    """
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)

    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)    # log them in straight away
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect_to_dashboard(user)
    else:
        form = RegisterForm()

    return render(request, "iipms_app/register.html", {"form": form})


def login_view(request):
    """
    GET:  Show the login form.
    POST: Check credentials and log the user in.
    """
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)

    error = ""

    if request.method == "POST":
        email    = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        # Django's authenticate checks email + password
        # We use username=email because we set up email login in forms.py
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            return redirect_to_dashboard(user)
        else:
            error = "Invalid email or password. Please try again."

    return render(request, "iipms_app/login.html", {"error": error})


@login_required
def logout_view(request):
    """Log the user out and go to the home page."""
    logout(request)
    return redirect("home")


# =============================================================
# STUDENT VIEWS
# =============================================================

@login_required
def student_dashboard(request):
    """
    The student's main page.
    Shows their profile, applications, notifications, offers, evaluations.
    """
    if not require_role(request, User.ROLE_STUDENT):
        return redirect_to_dashboard(request.user)

    user = request.user

    # Get or create the student's profile (so it always exists)
    profile, _ = StudentProfile.objects.get_or_create(user=user)

    # All the data for the dashboard tabs
    applications  = Application.objects.filter(student=user).order_by("-applied_at")
    notifications = Notification.objects.filter(recipient=user).order_by("-created_at")
    offers        = Offer.objects.filter(student=user).order_by("-created_at")
    evaluations   = Evaluation.objects.filter(student=user).order_by("-submitted_at")
    logs          = WeeklyLog.objects.filter(student=user).order_by("-submitted_at")

    # Count unread notifications for the badge
    unread_count  = notifications.filter(is_read=False).count()

    # All active internships for the Browse tab
    internships   = Internship.objects.filter(is_active=True).order_by("-created_at")

    # IDs of internships already applied to (so we can show "Applied" badge)
    applied_ids   = applications.values_list("internship_id", flat=True)

    context = {
        "profile":      profile,
        "applications": applications,
        "notifications": notifications,
        "offers":       offers,
        "evaluations":  evaluations,
        "logs":         logs,
        "unread_count": unread_count,
        "internships":  internships,
        "applied_ids":  list(applied_ids),
    }
    return render(request, "iipms_app/student_dashboard.html", context)


@login_required
def student_profile_edit(request):
    """
    Student updates their own profile (skills, preferences, CV, etc.)
    """
    if not require_role(request, User.ROLE_STUDENT):
        return redirect_to_dashboard(request.user)

    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            # Also update the user's name/phone if they changed it
            request.user.first_name = request.POST.get("first_name", request.user.first_name)
            request.user.last_name  = request.POST.get("last_name",  request.user.last_name)
            request.user.phone      = request.POST.get("phone",      request.user.phone)
            if request.FILES.get("photo"):
                request.user.photo = request.FILES["photo"]
            request.user.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("student_dashboard")
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, "iipms_app/student_profile_edit.html", {
        "form":    form,
        "profile": profile,
    })


@login_required
def internship_list(request):
    """
    Browse all active internships with search and skill-match scores.
    """
    if not require_role(request, User.ROLE_STUDENT):
        return redirect_to_dashboard(request.user)

    search = request.GET.get("q", "").strip()
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    # Start with all active internships
    jobs = Internship.objects.filter(is_active=True)

    # Apply search filter if the student typed something
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)   |
            Q(company__icontains=search) |
            Q(skills__icontains=search)  |
            Q(location__icontains=search)
        )

    # Calculate skill match score for each job
    jobs_with_scores = []
    applied_ids = Application.objects.filter(student=request.user).values_list("internship_id", flat=True)

    for job in jobs:
        result       = rank_internships_for_student(profile, [job])
        score        = result[0]["score"] if result else 0
        already_applied = job.id in applied_ids

        if score >= 70:
            bar_colour = "green"
        elif score >= 40:
            bar_colour = "orange"
        else:
            bar_colour = "red"

        jobs_with_scores.append({
            "job":            job,
            "score":          score,
            "bar_colour":     bar_colour,
            "already_applied": already_applied,
        })

    return render(request, "iipms_app/internships.html", {
        "jobs":   jobs_with_scores,
        "search": search,
    })


@login_required
def matches_view(request):
    """
    The student's personalised ranked internship recommendations.
    Uses the full matching engine with reasons.
    """
    if not require_role(request, User.ROLE_STUDENT):
        return redirect_to_dashboard(request.user)

    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    jobs        = Internship.objects.filter(is_active=True)
    ranked      = rank_internships_for_student(profile, jobs)
    applied_ids = Application.objects.filter(student=request.user).values_list("internship_id", flat=True)

    # Add colour and applied status to each result
    for r in ranked:
        r["bar_colour"] = (
            "green"  if r["score"] >= 70 else
            "orange" if r["score"] >= 40 else
            "red"
        )
        r["already_applied"] = r["internship"].id in applied_ids

    return render(request, "iipms_app/matches.html", {
        "ranked":  ranked,
        "profile": profile,
    })


@login_required
@require_POST
def apply_view(request, internship_id):
    """
    Student submits an application for one internship.
    Called via a form POST from the browse or matches page.
    """
    if not require_role(request, User.ROLE_STUDENT):
        return redirect("home")

    job = get_object_or_404(Internship, id=internship_id, is_active=True)

    # Check they haven't already applied
    if Application.objects.filter(student=request.user, internship=job).exists():
        messages.warning(request, "You have already applied for this internship.")
        return redirect("internship_list")

    # Get their current skills from their profile
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    # Create the application
    Application.objects.create(
        student         = request.user,
        internship      = job,
        skills_at_apply = profile.skills,
    )

    # Notify the employer
    try:
        send_notification(
            recipient = job.employer,
            from_name = request.user.get_full_name(),
            subject   = f"New Application: {job.title}",
            message   = (
                f"{request.user.get_full_name()} has applied for your internship: "
                f"{job.title}. Log in to view their application."
            ),
        )
    except Exception:
        pass  # don't crash if notification fails

    messages.success(request, f"Application submitted for {job.title}!")
    return redirect("internship_list")


@login_required
@require_POST
def withdraw_application(request, app_id):
    """Student withdraws their own application."""
    if not require_role(request, User.ROLE_STUDENT):
        return redirect("home")

    app = get_object_or_404(Application, id=app_id, student=request.user)
    app.status = Application.STATUS_WITHDRAWN
    app.save()

    messages.success(request, "Application withdrawn.")
    return redirect("student_dashboard")


@login_required
@require_POST
def respond_to_application(request, app_id):
    """
    Student accepts or declines an interview invitation or offer.
    """
    if not require_role(request, User.ROLE_STUDENT):
        return redirect("home")

    app      = get_object_or_404(Application, id=app_id, student=request.user)
    response = request.POST.get("response", "")

    valid_responses = [
        "Accepted Interview", "Declined Interview",
        "Accepted Offer",     "Declined Offer",
    ]

    if response in valid_responses:
        app.student_response = response
        app.save()
        messages.success(request, f"Response recorded: {response}")
    else:
        messages.error(request, "Invalid response.")

    return redirect("student_dashboard")


@login_required
@require_POST
def respond_to_offer(request, offer_id):
    """Student accepts or declines a formal offer letter."""
    if not require_role(request, User.ROLE_STUDENT):
        return redirect("home")

    offer    = get_object_or_404(Offer, id=offer_id, student=request.user)
    response = request.POST.get("response", "")

    if response == "Accepted":
        offer.status = Offer.STATUS_ACCEPTED
        offer.save()
        messages.success(request, "You have accepted the offer! Congratulations!")

        send_notification(
            recipient = offer.employer,
            from_name = request.user.get_full_name(),
            subject   = "Offer Accepted",
            message   = f"{request.user.get_full_name()} has accepted your offer for {offer.internship.title}.",
        )

    elif response == "Declined":
        offer.status = Offer.STATUS_DECLINED
        offer.save()
        messages.info(request, "You have declined the offer.")

    return redirect("student_dashboard")


@login_required
def weekly_log_view(request):
    """
    Student submits a weekly progress log.
    Shows their own logs below the form.
    """
    if not require_role(request, User.ROLE_STUDENT):
        return redirect_to_dashboard(request.user)

    # Pre-fill company from their most recent hired application
    hired_app   = Application.objects.filter(
        student=request.user,
        status__in=[Application.STATUS_HIRED]
    ).order_by("-applied_at").first()

    if request.method == "POST":
        form = WeeklyLogForm(request.POST)
        if form.is_valid():
            log          = form.save(commit=False)
            log.student  = request.user
            if hired_app:
                log.internship   = hired_app.internship
                log.company_name = hired_app.internship.company
            log.save()
            messages.success(request, "Weekly log submitted successfully!")
            return redirect("weekly_log")
    else:
        initial = {}
        if hired_app:
            initial["company_name"] = hired_app.internship.company
        form = WeeklyLogForm(initial=initial)

    logs = WeeklyLog.objects.filter(student=request.user).order_by("-submitted_at")

    return render(request, "iipms_app/weekly_log.html", {
        "form":      form,
        "logs":      logs,
        "hired_app": hired_app,
    })


@login_required
@require_POST
def mark_notification_read(request, notif_id):
    """Mark one notification as read."""
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    return redirect(request.META.get("HTTP_REFERER", "student_dashboard"))


@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark every notification as read for this user."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get("HTTP_REFERER", "student_dashboard"))


@login_required
@require_POST
def delete_notification(request, notif_id):
    """Permanently delete one notification."""
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.delete()
    return redirect(request.META.get("HTTP_REFERER", "student_dashboard"))


# =============================================================
# EMPLOYER VIEWS
# =============================================================

@login_required
def employer_dashboard(request):
    """
    Employer's main page: post jobs, view applications, see logs.
    """
    if not require_role(request, User.ROLE_EMPLOYER):
        return redirect_to_dashboard(request.user)

    profile, _ = EmployerProfile.objects.get_or_create(
        user=request.user,
        defaults={"company_name": request.user.get_full_name()},
    )

    # Stats for the top row
    my_jobs        = Internship.objects.filter(employer=request.user)
    my_app_ids     = Application.objects.filter(internship__employer=request.user)
    hired_count    = my_app_ids.filter(status=Application.STATUS_HIRED).count()
    my_logs        = WeeklyLog.objects.filter(company_name__iexact=profile.company_name)

    # Applications grouped for display
    applications   = my_app_ids.order_by("-applied_at")

    context = {
        "profile":      profile,
        "my_jobs":      my_jobs,
        "applications": applications,
        "hired_count":  hired_count,
        "my_logs":      my_logs,
    }
    return render(request, "iipms_app/employer_dashboard.html", context)


@login_required
def post_internship(request):
    """
    Employer creates a new internship listing.
    """
    if not require_role(request, User.ROLE_EMPLOYER):
        return redirect_to_dashboard(request.user)

    profile, _ = EmployerProfile.objects.get_or_create(
        user=request.user,
        defaults={"company_name": request.user.get_full_name()},
    )

    if request.method == "POST":
        form = InternshipForm(request.POST)
        if form.is_valid():
            job          = form.save(commit=False)
            job.employer = request.user
            job.company  = profile.company_name   # use verified company name
            job.save()
            messages.success(request, f"Internship '{job.title}' posted successfully!")
            return redirect("employer_dashboard")
    else:
        form = InternshipForm()

    return render(request, "iipms_app/post_internship.html", {"form": form})


@login_required
@require_POST
def update_application_status(request, app_id):
    """
    Employer moves an applicant through the pipeline:
    schedule interview, shortlist, hire, reject, etc.
    """
    if not require_role(request, User.ROLE_EMPLOYER):
        return redirect("home")

    # Make sure this application belongs to one of their jobs
    app = get_object_or_404(Application, id=app_id, internship__employer=request.user)

    new_status     = request.POST.get("status", "")
    interview_date = request.POST.get("interview_date", "")
    interview_note = request.POST.get("interview_note", "")

    valid_statuses = [
        Application.STATUS_PENDING,   Application.STATUS_REVIEW,
        Application.STATUS_INTERVIEW, Application.STATUS_SHORTLIST,
        Application.STATUS_REFERENCE, Application.STATUS_HIRED,
        Application.STATUS_REJECTED,
    ]

    if new_status not in valid_statuses:
        messages.error(request, "Invalid status.")
        return redirect("employer_dashboard")

    app.status = new_status
    if interview_date:
        app.interview_date = interview_date
    if interview_note:
        app.interview_note = interview_note
    app.save()

    # Notify the student
    subject = f"Application Update — {app.internship.title}"
    if new_status == Application.STATUS_INTERVIEW:
        subject  = f"Interview Scheduled — {app.internship.title}"
        msg_body = (
            f"Your interview for {app.internship.title} at {app.internship.company} "
            f"has been scheduled on {interview_date}. "
            + (f"Note: {interview_note}" if interview_note else "")
            + " Please accept or decline in your Student Portal."
        )
    elif new_status == Application.STATUS_HIRED:
        msg_body = (
            f"Congratulations! You have been selected for {app.internship.title} "
            f"at {app.internship.company}. Please accept or decline in your portal."
        )
    elif new_status == Application.STATUS_REJECTED:
        msg_body = (
            f"Thank you for applying to {app.internship.company}. "
            "Unfortunately we will not be progressing your application at this time."
        )
    else:
        msg_body = (
            f"Your application for {app.internship.title} at {app.internship.company} "
            f"has been updated to: {new_status}. Log in for details."
        )

    send_notification(
        recipient = app.student,
        from_name = app.internship.company,
        subject   = subject,
        message   = msg_body,
    )

    messages.success(request, f"Status updated to: {new_status}")
    return redirect("employer_dashboard")


@login_required
def issue_offer(request, app_id):
    """
    Employer issues a formal offer letter.
    The officer must approve it before the student sees it.
    """
    if not require_role(request, User.ROLE_EMPLOYER):
        return redirect_to_dashboard(request.user)

    app = get_object_or_404(Application, id=app_id, internship__employer=request.user)

    if request.method == "POST":
        form = OfferForm(request.POST)
        if form.is_valid():
            offer            = form.save(commit=False)
            offer.employer   = request.user
            offer.student    = app.student
            offer.internship = app.internship
            offer.save()

            # Notify the officer to approve
            officers = User.objects.filter(role=User.ROLE_OFFICER)
            for officer in officers:
                send_notification(
                    recipient = officer,
                    from_name = app.internship.company,
                    subject   = f"New Offer Awaiting Approval — {app.internship.title}",
                    message   = (
                        f"{app.internship.company} has issued an offer to "
                        f"{app.student.get_full_name()} for {app.internship.title}. "
                        "Please review and approve in the Officer Dashboard."
                    ),
                )

            messages.success(request, "Offer issued! Waiting for officer approval.")
            return redirect("employer_dashboard")
    else:
        form = OfferForm()

    return render(request, "iipms_app/issue_offer.html", {
        "form": form,
        "app":  app,
    })


@login_required
def submit_evaluation(request, student_id, internship_id):
    """
    Employer (or supervisor) submits a performance evaluation for a student.
    """
    if not require_role(request, User.ROLE_EMPLOYER, User.ROLE_SUPERVISOR):
        return redirect_to_dashboard(request.user)

    student    = get_object_or_404(User, id=student_id, role=User.ROLE_STUDENT)
    internship = get_object_or_404(Internship, id=internship_id)

    from_role = (
        Evaluation.FROM_EMPLOYER
        if request.user.is_employer()
        else Evaluation.FROM_SUPERVISOR
    )

    if request.method == "POST":
        form = EvaluationForm(request.POST)
        if form.is_valid():
            ev            = form.save(commit=False)
            ev.evaluator  = request.user
            ev.student    = student
            ev.internship = internship
            ev.from_role  = from_role
            ev.save()

            send_notification(
                recipient = student,
                from_name = request.user.get_full_name(),
                subject   = f"New Evaluation — {internship.title}",
                message   = (
                    f"An evaluation has been submitted for your internship at "
                    f"{internship.company}. View it in your Student Portal."
                ),
            )

            messages.success(request, "Evaluation submitted successfully!")
            return redirect("employer_dashboard")
    else:
        form = EvaluationForm()

    return render(request, "iipms_app/submit_evaluation.html", {
        "form":      form,
        "student":   student,
        "internship": internship,
    })


# =============================================================
# PLACEMENT OFFICER VIEWS
# =============================================================

@login_required
def officer_dashboard(request):
    """
    Placement officer's main dashboard.
    Shows statistics and all the tabs for managing the system.
    """
    if not require_role(request, User.ROLE_OFFICER):
        return redirect_to_dashboard(request.user)

    # Stats for the top row
    student_count     = User.objects.filter(role=User.ROLE_STUDENT).count()
    internship_count  = Internship.objects.filter(is_active=True).count()
    application_count = Application.objects.count()
    placed_count      = Application.objects.filter(status=Application.STATUS_HIRED).count()

    # Data for each tab
    all_students      = User.objects.filter(role=User.ROLE_STUDENT).order_by("first_name")
    all_applications  = Application.objects.select_related("student", "internship").order_by("-applied_at")
    all_logs          = WeeklyLog.objects.select_related("student").order_by("-submitted_at")
    verify_requests   = EmployerProfile.objects.filter(verification_status="Pending").select_related("user")
    all_offers        = Offer.objects.select_related("employer", "student", "internship").order_by("-created_at")
    progress_entries  = ProgressEntry.objects.select_related("student", "internship").order_by("-created_at")
    all_evaluations   = Evaluation.objects.select_related("evaluator", "student", "internship").order_by("-submitted_at")
    completions       = Completion.objects.select_related("student", "internship").order_by("-recorded_at")
    assignments       = SupervisorAssignment.objects.select_related("student", "supervisor").order_by("-assigned_at")
    supervisors       = User.objects.filter(role=User.ROLE_SUPERVISOR).order_by("first_name")
    student_profiles  = StudentProfile.objects.select_related("user").all()

    context = {
        "student_count":     student_count,
        "internship_count":  internship_count,
        "application_count": application_count,
        "placed_count":      placed_count,
        "all_students":      all_students,
        "all_applications":  all_applications,
        "all_logs":          all_logs,
        "verify_requests":   verify_requests,
        "all_offers":        all_offers,
        "progress_entries":  progress_entries,
        "all_evaluations":   all_evaluations,
        "completions":       completions,
        "assignments":       assignments,
        "supervisors":       supervisors,
        "student_profiles":  student_profiles,
    }
    return render(request, "iipms_app/officer_dashboard.html", context)


@login_required
@require_POST
def officer_verify_employer(request, profile_id):
    """Officer approves or rejects an employer verification request."""
    if not require_role(request, User.ROLE_OFFICER):
        return redirect("home")

    profile    = get_object_or_404(EmployerProfile, id=profile_id)
    new_status = request.POST.get("status", "")

    if new_status in ["Approved", "Rejected"]:
        profile.verification_status = new_status
        profile.verified_by         = request.user
        profile.verified_at         = timezone.now()
        profile.save()

        send_notification(
            recipient = profile.user,
            from_name = "IIPMS Placement Team",
            subject   = f"Employer Verification {new_status}",
            message   = (
                f"Your company verification for {profile.company_name} has been "
                f"{new_status.lower()} by the placement team. "
                + ("You can now post internship listings." if new_status == "Approved" else
                   "Please contact the placement office for more information.")
            ),
        )

        messages.success(request, f"Verification {new_status} for {profile.company_name}.")

    return redirect("officer_dashboard")


@login_required
@require_POST
def officer_set_next_step(request, app_id):
    """Officer sets a next step on a student's application."""
    if not require_role(request, User.ROLE_OFFICER):
        return redirect("home")

    app       = get_object_or_404(Application, id=app_id)
    next_step = request.POST.get("next_step", "")
    note      = request.POST.get("note", "")

    app.officer_next_step = next_step
    app.officer_note      = note
    app.save()

    # Notify the student
    send_notification(
        recipient = app.student,
        from_name = "Placement Office",
        subject   = f"Next Step — {app.internship.title}",
        message   = (
            f"The placement officer has set a next step for your application to "
            f"{app.internship.title}: {next_step}. "
            + (f"Note: {note}" if note else "")
        ),
    )

    messages.success(request, "Next step set and student notified.")
    return redirect("officer_dashboard")


@login_required
@require_POST
def officer_approve_offer(request, offer_id):
    """Officer approves a formal offer — it then becomes visible to the student."""
    if not require_role(request, User.ROLE_OFFICER):
        return redirect("home")

    offer  = get_object_or_404(Offer, id=offer_id)
    action = request.POST.get("action", "")

    if action == "approve":
        offer.officer_approved = True
        offer.status           = Offer.STATUS_APPROVED
        offer.approved_by      = request.user
        offer.approved_at      = timezone.now()
        offer.save()

        send_notification(
            recipient = offer.student,
            from_name = "Placement Office",
            subject   = f"Internship Offer Approved — {offer.internship.title}",
            message   = (
                f"An internship offer for {offer.internship.title} at "
                f"{offer.internship.company} has been approved by the placement officer. "
                "Please check your Offers tab to accept or decline."
            ),
        )
        messages.success(request, "Offer approved and student notified.")

    elif action == "reject":
        offer.status = Offer.STATUS_REJECTED
        offer.save()

        send_notification(
            recipient = offer.student,
            from_name = "Placement Office",
            subject   = "Internship Offer — Update",
            message   = (
                f"An offer for {offer.internship.title} was not approved by the "
                "placement officer. Please contact the placement office for more details."
            ),
        )
        messages.info(request, "Offer rejected.")

    return redirect("officer_dashboard")


@login_required
@require_POST
def officer_add_progress(request):
    """Officer logs a progress stage for a student."""
    if not require_role(request, User.ROLE_OFFICER):
        return redirect("home")

    student_id    = request.POST.get("student_id")
    internship_id = request.POST.get("internship_id")
    stage         = request.POST.get("stage")
    notes         = request.POST.get("notes", "")

    student    = get_object_or_404(User, id=student_id, role=User.ROLE_STUDENT)
    internship = Internship.objects.filter(id=internship_id).first()

    ProgressEntry.objects.create(
        student    = student,
        internship = internship,
        stage      = stage,
        notes      = notes,
        set_by     = request.user,
    )

    send_notification(
        recipient = student,
        from_name = "Placement Office",
        subject   = f"Progress Update — {stage}",
        message   = (
            f"Your internship placement stage has been updated to: {stage}. "
            + (f"Note: {notes}" if notes else "")
        ),
    )

    messages.success(request, f"Progress entry added: {stage}")
    return redirect("officer_dashboard")


@login_required
@require_POST
def officer_assign_supervisor(request):
    """Officer links a student to an academic supervisor."""
    if not require_role(request, User.ROLE_OFFICER):
        return redirect("home")

    student_id    = request.POST.get("student_id")
    supervisor_id = request.POST.get("supervisor_id")

    student    = get_object_or_404(User, id=student_id,    role=User.ROLE_STUDENT)
    supervisor = get_object_or_404(User, id=supervisor_id, role=User.ROLE_SUPERVISOR)

    # Don't create a duplicate assignment
    if not SupervisorAssignment.objects.filter(student=student, supervisor=supervisor).exists():
        SupervisorAssignment.objects.create(
            student    = student,
            supervisor = supervisor,
            assigned_by = request.user,
        )

        send_notification(
            recipient = supervisor,
            from_name = request.user.get_full_name() + " (Placement Officer)",
            subject   = f"Student Assigned: {student.get_full_name()}",
            message   = (
                f"{student.get_full_name()} has been assigned to you as their "
                "academic supervisor. Log in to monitor their progress."
            ),
        )

        send_notification(
            recipient = student,
            from_name = request.user.get_full_name() + " (Placement Officer)",
            subject   = "Academic Supervisor Assigned",
            message   = (
                f"You have been assigned an academic supervisor: "
                f"{supervisor.get_full_name()}. They will monitor your internship progress."
            ),
        )

        messages.success(request, f"{supervisor.get_full_name()} assigned to {student.get_full_name()}.")
    else:
        messages.warning(request, "This assignment already exists.")

    return redirect("officer_dashboard")


@login_required
@require_POST
def officer_mark_complete(request):
    """Officer marks a student's internship as officially complete."""
    if not require_role(request, User.ROLE_OFFICER):
        return redirect("home")

    student_id      = request.POST.get("student_id")
    internship_id   = request.POST.get("internship_id")
    completion_date = request.POST.get("completion_date", "")

    student    = get_object_or_404(User, id=student_id,    role=User.ROLE_STUDENT)
    internship = get_object_or_404(Internship, id=internship_id)

    Completion.objects.create(
        student         = student,
        internship      = internship,
        completion_date = completion_date,
        recorded_by     = request.user,
    )

    send_notification(
        recipient = student,
        from_name = "Placement Office",
        subject   = "🎓 Internship Completion Recorded",
        message   = (
            f"Your internship at {internship.company} has been marked as complete "
            f"as of {completion_date}. Congratulations on completing your internship!"
        ),
    )

    messages.success(request, f"Completion recorded for {student.get_full_name()}.")
    return redirect("officer_dashboard")


@login_required
def reports_view(request):
    """
    Analytics and reporting page for the placement officer.
    """
    if not require_role(request, User.ROLE_OFFICER):
        return redirect_to_dashboard(request.user)

    # Placement rate
    total_students  = User.objects.filter(role=User.ROLE_STUDENT).count()
    placed_students = Application.objects.filter(
        status=Application.STATUS_HIRED
    ).values("student").distinct().count()

    placement_rate  = round((placed_students / total_students * 100) if total_students else 0, 1)

    # Application status breakdown
    status_counts = (
        Application.objects
        .values("status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Top employers by applications
    top_employers = (
        Application.objects
        .values("internship__company")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    # Weekly log activity
    log_count = WeeklyLog.objects.count()

    # Completion count
    completion_count = Completion.objects.count()

    context = {
        "total_students":   total_students,
        "placed_students":  placed_students,
        "placement_rate":   placement_rate,
        "status_counts":    status_counts,
        "top_employers":    top_employers,
        "log_count":        log_count,
        "completion_count": completion_count,
        "all_applications": Application.objects.select_related("student", "internship").order_by("-applied_at"),
    }
    return render(request, "iipms_app/reports.html", context)


@login_required
def export_csv(request):
    """
    Download a CSV file of all applications.
    Only the placement officer can do this.
    """
    if not require_role(request, User.ROLE_OFFICER):
        return redirect("home")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="iipms_applications.csv"'

    writer = csv.writer(response)
    writer.writerow(["Student", "Email", "Internship", "Company", "Status", "Applied At"])

    for app in Application.objects.select_related("student", "internship").order_by("-applied_at"):
        writer.writerow([
            app.student.get_full_name(),
            app.student.email,
            app.internship.title,
            app.internship.company,
            app.status,
            app.applied_at.strftime("%d/%m/%Y %H:%M"),
        ])

    return response


# =============================================================
# SUPERVISOR VIEWS
# =============================================================

@login_required
def supervisor_dashboard(request):
    """
    Academic supervisor's dashboard.
    Shows the students assigned to them and lets them submit evaluations.
    """
    if not require_role(request, User.ROLE_SUPERVISOR):
        return redirect_to_dashboard(request.user)

    # Find students assigned to this supervisor
    assignments = SupervisorAssignment.objects.filter(
        supervisor=request.user
    ).select_related("student")

    assigned_students = [a.student for a in assignments]

    # Their logs and evaluations
    logs = WeeklyLog.objects.filter(
        student__in=assigned_students
    ).order_by("-submitted_at")

    evaluations_given = Evaluation.objects.filter(
        evaluator=request.user
    ).order_by("-submitted_at")

    return render(request, "iipms_app/supervisor_dashboard.html", {
        "assignments":       assignments,
        "assigned_students": assigned_students,
        "logs":              logs,
        "evaluations_given": evaluations_given,
    })


# =============================================================
# API ENDPOINTS (JSON — for AJAX calls from the HTML frontend)
# =============================================================

@login_required
def api_internships(request):
    """
    Return all active internships as JSON with match scores.
    This is called by the existing JS frontend to load job cards.
    """
    search  = request.GET.get("q", "").lower()
    jobs    = Internship.objects.filter(is_active=True)

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(company__icontains=search) |
            Q(skills__icontains=search)
        )

    profile = None
    if request.user.is_student():
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    applied_ids = []
    if request.user.is_student():
        applied_ids = list(
            Application.objects.filter(student=request.user).values_list("internship_id", flat=True)
        )

    result = []
    for job in jobs:
        score = 0
        if profile:
            match_result = rank_internships_for_student(profile, [job])
            score        = match_result[0]["score"] if match_result else 0

        result.append({
            "id":       job.id,
            "title":    job.title,
            "company":  job.company,
            "location": job.location,
            "duration": job.duration,
            "skills":   job.skills,
            "stipend":  job.stipend,
            "industry": job.industry,
            "description": job.description,
            "score":    score,
            "applied":  job.id in applied_ids,
        })

    return JsonResponse({"internships": result})


@login_required
def api_notifications(request):
    """Return unread notification count as JSON."""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({"unread_count": count})
