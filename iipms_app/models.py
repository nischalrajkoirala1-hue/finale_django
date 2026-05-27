# =============================================================
# models.py
# This file defines every database table in the IIPMS system.
# Each class here becomes one table in the database.
# Django reads these classes and creates the SQL for us.
# =============================================================

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# -------------------------------------------------------------
# USER MODEL
# We extend Django's built-in user so we can add our own fields
# like role, skills, and profile photo.
# -------------------------------------------------------------

class User(AbstractUser):
    """
    One row per registered person.
    The 'role' field controls which dashboard they see.
    We keep Django's built-in username, email, password fields
    and add everything else we need below.
    """

    # The four roles in the system
    ROLE_STUDENT    = "student"
    ROLE_EMPLOYER   = "employer"
    ROLE_OFFICER    = "officer"
    ROLE_SUPERVISOR = "supervisor"

    ROLE_CHOICES = [
        (ROLE_STUDENT,    "Student"),
        (ROLE_EMPLOYER,   "Employer / Industry Partner"),
        (ROLE_OFFICER,    "Placement Officer"),
        (ROLE_SUPERVISOR, "Academic Supervisor"),
    ]

    # Every user has a role
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
    )

    # Profile photo (stored on the server, optional)
    photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
    )

    # Phone number (optional)
    phone = models.CharField(max_length=20, blank=True, default="")

    def __str__(self):
        # This shows a readable name in the Django admin panel
        return f"{self.get_full_name()} ({self.role})"

    def is_student(self):
        return self.role == self.ROLE_STUDENT

    def is_employer(self):
        return self.role == self.ROLE_EMPLOYER

    def is_officer(self):
        return self.role == self.ROLE_OFFICER

    def is_supervisor(self):
        return self.role == self.ROLE_SUPERVISOR


# -------------------------------------------------------------
# STUDENT PROFILE
# Extra information that only students have.
# One StudentProfile per student User.
# -------------------------------------------------------------

class StudentProfile(models.Model):
    """
    All the extra details about a student.
    Linked to the User table with a OneToOneField
    (one student = one profile, one profile = one student).
    """

    # Link to the user account
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,   # if the user is deleted, delete this profile too
        related_name="student_profile",
    )

    # Academic details
    course       = models.CharField(max_length=200, blank=True, default="")
    wam          = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    availability = models.CharField(max_length=100, blank=True, default="")  # e.g. "July 2026"

    # Skills stored as comma-separated text, e.g. "Python, SQL, Django"
    skills = models.TextField(blank=True, default="")

    # Preferences for matching
    INDUSTRY_CHOICES = [
        ("",           "No preference"),
        ("Technology", "Technology / IT"),
        ("Finance",    "Finance / Banking"),
        ("Healthcare", "Healthcare"),
        ("Engineering","Engineering"),
        ("Marketing",  "Marketing"),
        ("Education",  "Education"),
        ("Any",        "Open to Any"),
    ]

    WORK_TYPE_CHOICES = [
        ("",         "No preference"),
        ("Remote",   "Remote"),
        ("On-site",  "On-site"),
        ("Hybrid",   "Hybrid"),
        ("Any",      "No preference"),
    ]

    industry_pref  = models.CharField(max_length=50, blank=True, default="", choices=INDUSTRY_CHOICES)
    work_type      = models.CharField(max_length=20, blank=True, default="", choices=WORK_TYPE_CHOICES)
    location_pref  = models.CharField(max_length=100, blank=True, default="")

    # CV file upload
    cv_file = models.FileField(upload_to="cvs/", blank=True, null=True)

    # Flags set by placement officer
    is_eligible   = models.BooleanField(default=False)
    has_work_rights = models.BooleanField(default=True)
    eligibility_notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Profile: {self.user.get_full_name()}"

    def skills_list(self):
        """Return skills as a Python list, stripping whitespace."""
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(",") if s.strip()]


# -------------------------------------------------------------
# EMPLOYER PROFILE
# Extra information that only employers have.
# -------------------------------------------------------------

class EmployerProfile(models.Model):
    """
    Company details for employer accounts.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employer_profile",
    )

    company_name = models.CharField(max_length=200)
    industry     = models.CharField(max_length=100, blank=True, default="")
    website      = models.CharField(max_length=200, blank=True, default="")
    abn          = models.CharField(max_length=20,  blank=True, default="")  # Australian Business Number

    # Verification status — set by placement officer
    VERIFY_PENDING  = "Pending"
    VERIFY_APPROVED = "Approved"
    VERIFY_REJECTED = "Rejected"

    VERIFY_CHOICES = [
        (VERIFY_PENDING,  "Pending"),
        (VERIFY_APPROVED, "Approved"),
        (VERIFY_REJECTED, "Rejected"),
    ]

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFY_CHOICES,
        default=VERIFY_PENDING,
    )
    verification_notes  = models.TextField(blank=True, default="")
    verified_by         = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="verifications_done",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.company_name


# -------------------------------------------------------------
# SUPERVISOR PROFILE
# Extra information for academic supervisors.
# -------------------------------------------------------------

class SupervisorProfile(models.Model):
    """
    University/supervisor details.
    """

    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name="supervisor_profile")
    university  = models.CharField(max_length=200, blank=True, default="")
    department  = models.CharField(max_length=200, blank=True, default="")

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.university}"


# -------------------------------------------------------------
# INTERNSHIP LISTING
# Each row is one job posted by an employer.
# -------------------------------------------------------------

class Internship(models.Model):
    """
    One row per internship opportunity.
    Employers create these; students apply to them.
    """

    # Which employer posted this listing
    employer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posted_internships",
        limit_choices_to={"role": "employer"},
    )

    title       = models.CharField(max_length=200)
    company     = models.CharField(max_length=200)   # copied from employer profile for easy display
    location    = models.CharField(max_length=100)
    duration    = models.CharField(max_length=100, blank=True, default="")  # e.g. "3 months"
    description = models.TextField(blank=True, default="")
    skills      = models.TextField(blank=True, default="")   # comma-separated required skills
    stipend     = models.CharField(max_length=100, blank=True, default="")
    industry    = models.CharField(max_length=100, blank=True, default="")

    WORK_TYPE_CHOICES = [
        ("Remote",  "Remote"),
        ("On-site", "On-site"),
        ("Hybrid",  "Hybrid"),
    ]
    work_type   = models.CharField(max_length=20, blank=True, default="", choices=WORK_TYPE_CHOICES)

    start_date  = models.CharField(max_length=100, blank=True, default="")
    end_date    = models.CharField(max_length=100, blank=True, default="")

    # Whether this listing is still open for applications
    is_active   = models.BooleanField(default=True)

    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.company}"

    def skills_list(self):
        """Return the required skills as a Python list."""
        if not self.skills:
            return []
        return [s.strip().lower() for s in self.skills.split(",") if s.strip()]


# -------------------------------------------------------------
# APPLICATION
# A student applies to an internship — one row per application.
# -------------------------------------------------------------

class Application(models.Model):
    """
    Tracks each time a student applies to an internship.
    """

    student    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications",
                                   limit_choices_to={"role": "student"})
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name="applications")

    # Status pipeline — updated by employer and officer
    STATUS_PENDING   = "Pending"
    STATUS_REVIEW    = "Under Review"
    STATUS_INTERVIEW = "Interview Scheduled"
    STATUS_SHORTLIST = "Shortlisted"
    STATUS_REFERENCE = "Reference Check"
    STATUS_OFFER     = "Offer Extended"
    STATUS_HIRED     = "Hired"
    STATUS_REJECTED  = "Rejected"
    STATUS_WITHDRAWN = "Withdrawn"

    STATUS_CHOICES = [
        (STATUS_PENDING,   "Pending"),
        (STATUS_REVIEW,    "Under Review"),
        (STATUS_INTERVIEW, "Interview Scheduled"),
        (STATUS_SHORTLIST, "Shortlisted"),
        (STATUS_REFERENCE, "Reference Check"),
        (STATUS_OFFER,     "Offer Extended"),
        (STATUS_HIRED,     "Hired"),
        (STATUS_REJECTED,  "Rejected"),
        (STATUS_WITHDRAWN, "Withdrawn"),
    ]

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Interview scheduling fields (filled in by employer)
    interview_date = models.CharField(max_length=100, blank=True, default="")
    interview_note = models.TextField(blank=True, default="")

    # Student's response to an interview or offer
    RESPONSE_CHOICES = [
        ("",                  "No response yet"),
        ("Accepted Interview", "Accepted Interview"),
        ("Declined Interview", "Declined Interview"),
        ("Accepted Offer",    "Accepted Offer"),
        ("Declined Offer",    "Declined Offer"),
    ]
    student_response = models.CharField(max_length=30, blank=True, default="", choices=RESPONSE_CHOICES)

    # Officer can set a next step and add a note
    officer_next_step = models.CharField(max_length=200, blank=True, default="")
    officer_note      = models.TextField(blank=True, default="")

    # Skills the student listed at time of application
    skills_at_apply   = models.TextField(blank=True, default="")

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A student can only apply once to each internship
        unique_together = ("student", "internship")

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.internship.title}"


# -------------------------------------------------------------
# WEEKLY LOG
# Students submit one of these per week during their internship.
# -------------------------------------------------------------

class WeeklyLog(models.Model):
    """
    A student's progress report for one week of their internship.
    Visible to their employer and the placement officer.
    """

    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="weekly_logs",
                                    limit_choices_to={"role": "student"})
    internship  = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name="weekly_logs",
                                    null=True, blank=True)
    company_name = models.CharField(max_length=200, blank=True, default="")

    week_number  = models.PositiveIntegerField()
    hours_worked = models.PositiveIntegerField()
    tasks        = models.TextField()         # what they did
    challenges   = models.TextField(blank=True, default="")
    reflection   = models.TextField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student.get_full_name()} — Week {self.week_number}"


# -------------------------------------------------------------
# OFFER LETTER
# Employer issues a formal offer; officer approves; student accepts.
# -------------------------------------------------------------

class Offer(models.Model):
    """
    A formal internship offer from an employer to a student.
    Goes through an officer approval step before the student sees it.
    """

    employer   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers_sent",
                                   limit_choices_to={"role": "employer"})
    student    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers_received",
                                   limit_choices_to={"role": "student"})
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name="offers")

    start_date = models.CharField(max_length=100)
    end_date   = models.CharField(max_length=100)
    stipend    = models.CharField(max_length=100, blank=True, default="")
    terms      = models.TextField(blank=True, default="")

    # Officer approval
    officer_approved = models.BooleanField(default=False)
    approved_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name="approved_offers")
    approved_at      = models.DateTimeField(null=True, blank=True)

    # Student response
    STATUS_PENDING  = "Awaiting Officer Approval"
    STATUS_APPROVED = "Awaiting Student Acceptance"
    STATUS_ACCEPTED = "Accepted"
    STATUS_DECLINED = "Declined"
    STATUS_REJECTED = "Rejected by Officer"

    STATUS_CHOICES = [
        (STATUS_PENDING,  "Awaiting Officer Approval"),
        (STATUS_APPROVED, "Awaiting Student Acceptance"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_DECLINED, "Declined"),
        (STATUS_REJECTED, "Rejected by Officer"),
    ]

    status     = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer: {self.student.get_full_name()} — {self.internship.title}"


# -------------------------------------------------------------
# EVALUATION
# Employers and supervisors rate the student after the internship.
# -------------------------------------------------------------

class Evaluation(models.Model):
    """
    A performance review submitted by an employer or supervisor.
    The student can view their own evaluations.
    """

    FROM_EMPLOYER    = "Employer"
    FROM_SUPERVISOR  = "Academic Supervisor"

    FROM_ROLE_CHOICES = [
        (FROM_EMPLOYER,   "Employer"),
        (FROM_SUPERVISOR, "Academic Supervisor"),
    ]

    evaluator  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations_given")
    student    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations_received",
                                   limit_choices_to={"role": "student"})
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name="evaluations")
    from_role  = models.CharField(max_length=30, choices=FROM_ROLE_CHOICES)

    # Ratings from 1 to 5
    rating_conduct       = models.IntegerField(default=3)
    rating_technical     = models.IntegerField(default=3)
    rating_communication = models.IntegerField(default=3)
    rating_overall       = models.IntegerField(default=3)

    comments       = models.TextField(blank=True, default="")
    recommendation = models.CharField(max_length=100, blank=True, default="")

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Eval of {self.student.get_full_name()} by {self.evaluator.get_full_name()}"


# -------------------------------------------------------------
# NOTIFICATION
# In-app messages sent between users.
# -------------------------------------------------------------

class Notification(models.Model):
    """
    One notification message sent to one user.
    Unread notifications show a badge in the navbar.
    """

    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    from_name   = models.CharField(max_length=200)    # name of sender (free text)
    subject     = models.CharField(max_length=200)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"To: {self.recipient.username} | {self.subject}"


# -------------------------------------------------------------
# PROGRESS ENTRY
# Officer logs a stage for a student (e.g. "Applied", "Placed").
# -------------------------------------------------------------

class ProgressEntry(models.Model):
    """
    A record of where a student is in the placement process.
    The officer adds these entries to track progress.
    """

    student    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress_entries",
                                   limit_choices_to={"role": "student"})
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name="progress_entries",
                                   null=True, blank=True)

    STAGE_CHOICES = [
        ("Applied",    "Applied"),
        ("Interview",  "Interview"),
        ("Offer",      "Offer"),
        ("Placed",     "Placed"),
        ("Withdrawn",  "Withdrawn"),
        ("Completed",  "Completed"),
    ]

    stage  = models.CharField(max_length=30, choices=STAGE_CHOICES)
    notes  = models.TextField(blank=True, default="")
    set_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name="progress_entries_set")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.get_full_name()} — {self.stage}"


# -------------------------------------------------------------
# SUPERVISOR ASSIGNMENT
# Placement officer assigns a supervisor to a student.
# -------------------------------------------------------------

class SupervisorAssignment(models.Model):
    """
    Links one student to one academic supervisor.
    Set by the placement officer.
    """

    student    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supervisor_assignments",
                                   limit_choices_to={"role": "student"})
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_students",
                                   limit_choices_to={"role": "supervisor"})
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assignments_made")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "supervisor")

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.supervisor.get_full_name()}"


# -------------------------------------------------------------
# INTERNSHIP COMPLETION
# Officer marks an internship as officially complete.
# -------------------------------------------------------------

class Completion(models.Model):
    """
    Records when a student finishes their internship.
    The placement officer sets this.
    """

    student          = models.ForeignKey(User, on_delete=models.CASCADE, related_name="completions",
                                         limit_choices_to={"role": "student"})
    internship       = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name="completions")
    completion_date  = models.CharField(max_length=100)
    recorded_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name="completions_recorded")
    recorded_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.get_full_name()} completed {self.internship.title}"
