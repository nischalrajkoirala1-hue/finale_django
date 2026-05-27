# =============================================================
# management/commands/seed_data.py
# A custom Django management command that creates demo data
# so you can log in and see the system working immediately.
#
# HOW TO RUN:
#     python manage.py seed_data
#
# This creates:
#   - 1 placement officer account
#   - 2 student accounts
#   - 1 employer account
#   - 1 supervisor account
#   - 4 internship listings
#   - Sample applications, logs, and notifications
# =============================================================

from django.core.management.base import BaseCommand
from django.utils                 import timezone
from iipms_app.models import (
    User, StudentProfile, EmployerProfile, SupervisorProfile,
    Internship, Application, WeeklyLog, Notification, ProgressEntry,
)


class Command(BaseCommand):
    help = "Seed the database with demo users, internships, and applications"

    def handle(self, *args, **kwargs):
        self.stdout.write("🌱 Seeding demo data...")

        # ── Placement Officer ──────────────────────────────────
        officer, created = User.objects.get_or_create(
            email    = "officer@iipms.edu.au",
            defaults = {
                "username":   "officer",
                "first_name": "Sarah",
                "last_name":  "Chen",
                "role":       User.ROLE_OFFICER,
                "is_staff":   True,   # can access /admin/ too
            },
        )
        if created:
            officer.set_password("officer123")
            officer.save()
            self.stdout.write("  ✓ Officer: officer@iipms.edu.au / officer123")
        else:
            self.stdout.write("  → Officer already exists")

        # ── Employer ───────────────────────────────────────────
        employer, created = User.objects.get_or_create(
            email    = "hr@techcorp.com.au",
            defaults = {
                "username":   "techcorp_hr",
                "first_name": "Michael",
                "last_name":  "Taylor",
                "role":       User.ROLE_EMPLOYER,
            },
        )
        if created:
            employer.set_password("employer123")
            employer.save()
            EmployerProfile.objects.create(
                user                = employer,
                company_name        = "TechCorp",
                industry            = "Technology",
                website             = "www.techcorp.com.au",
                abn                 = "12 345 678 901",
                verification_status = "Approved",
                verified_by         = officer,
            )
            self.stdout.write("  ✓ Employer: hr@techcorp.com.au / employer123")
        else:
            self.stdout.write("  → Employer already exists")

        # ── Academic Supervisor ────────────────────────────────
        supervisor, created = User.objects.get_or_create(
            email    = "supervisor@university.edu.au",
            defaults = {
                "username":   "supervisor_james",
                "first_name": "James",
                "last_name":  "Wong",
                "role":       User.ROLE_SUPERVISOR,
            },
        )
        if created:
            supervisor.set_password("super123")
            supervisor.save()
            SupervisorProfile.objects.create(
                user       = supervisor,
                university = "University of Technology Sydney",
                department = "School of Computer Science",
            )
            self.stdout.write("  ✓ Supervisor: supervisor@university.edu.au / super123")
        else:
            self.stdout.write("  → Supervisor already exists")

        # ── Student 1 ──────────────────────────────────────────
        student1, created = User.objects.get_or_create(
            email    = "alice@student.edu.au",
            defaults = {
                "username":   "alice_student",
                "first_name": "Alice",
                "last_name":  "Nguyen",
                "role":       User.ROLE_STUDENT,
            },
        )
        if created:
            student1.set_password("student123")
            student1.save()
            StudentProfile.objects.create(
                user          = student1,
                course        = "Bachelor of Computer Science",
                wam           = 75.5,
                availability  = "July 2026",
                skills        = "Python, Django, SQL, JavaScript, HTML, CSS",
                industry_pref = "Technology",
                work_type     = "Hybrid",
                location_pref = "Sydney",
                is_eligible   = True,
            )
            self.stdout.write("  ✓ Student 1: alice@student.edu.au / student123")
        else:
            self.stdout.write("  → Student 1 already exists")

        # ── Student 2 ──────────────────────────────────────────
        student2, created = User.objects.get_or_create(
            email    = "bob@student.edu.au",
            defaults = {
                "username":   "bob_student",
                "first_name": "Bob",
                "last_name":  "Smith",
                "role":       User.ROLE_STUDENT,
            },
        )
        if created:
            student2.set_password("student123")
            student2.save()
            StudentProfile.objects.create(
                user          = student2,
                course        = "Bachelor of Data Science",
                wam           = 68.0,
                availability  = "February 2026",
                skills        = "Python, SQL, Excel, Tableau, R",
                industry_pref = "Finance",
                work_type     = "Remote",
                location_pref = "Melbourne",
                is_eligible   = True,
            )
            self.stdout.write("  ✓ Student 2: bob@student.edu.au / student123")
        else:
            self.stdout.write("  → Student 2 already exists")

        # ── Internship Listings ────────────────────────────────
        jobs_data = [
            {
                "title":       "Frontend Developer Intern",
                "location":    "Sydney",
                "duration":    "3 months",
                "skills":      "HTML, CSS, JavaScript, React",
                "description": "Work with our frontend team building React components.",
                "industry":    "Technology",
                "work_type":   "Hybrid",
                "stipend":     "$600/week",
                "start_date":  "1 July 2026",
                "end_date":    "30 September 2026",
            },
            {
                "title":       "Backend Developer Intern",
                "location":    "Sydney",
                "duration":    "3 months",
                "skills":      "Python, Django, SQL, Git",
                "description": "Join our backend team working on Django REST APIs.",
                "industry":    "Technology",
                "work_type":   "On-site",
                "stipend":     "$650/week",
                "start_date":  "1 July 2026",
                "end_date":    "30 September 2026",
            },
            {
                "title":       "Data Analyst Intern",
                "location":    "Melbourne",
                "duration":    "6 months",
                "skills":      "Python, SQL, Excel, Tableau",
                "description": "Analyse customer data and build dashboards.",
                "industry":    "Technology",
                "work_type":   "Remote",
                "stipend":     "$550/week",
                "start_date":  "1 February 2026",
                "end_date":    "31 July 2026",
            },
            {
                "title":       "UI/UX Design Intern",
                "location":    "Remote",
                "duration":    "3 months",
                "skills":      "Figma, CSS, HTML",
                "description": "Design and prototype user interfaces for our mobile app.",
                "industry":    "Technology",
                "work_type":   "Remote",
                "stipend":     "Unpaid",
                "start_date":  "1 July 2026",
                "end_date":    "30 September 2026",
            },
        ]

        emp_profile = EmployerProfile.objects.filter(user=employer).first()
        company_name = emp_profile.company_name if emp_profile else "TechCorp"

        created_jobs = []
        for data in jobs_data:
            job, created = Internship.objects.get_or_create(
                title    = data["title"],
                employer = employer,
                defaults = {**data, "company": company_name},
            )
            created_jobs.append(job)
            if created:
                self.stdout.write(f"  ✓ Internship: {job.title}")
            else:
                self.stdout.write(f"  → Internship already exists: {job.title}")

        # ── Sample Application ─────────────────────────────────
        if created_jobs:
            app, created = Application.objects.get_or_create(
                student    = student1,
                internship = created_jobs[1],  # Backend Developer Intern
                defaults   = {
                    "status":          Application.STATUS_INTERVIEW,
                    "interview_date":  "15 June 2026 at 10:00 AM",
                    "interview_note":  "Via Zoom. Please prepare a code sample.",
                    "skills_at_apply": "Python, Django, SQL, JavaScript, HTML, CSS",
                },
            )
            if created:
                self.stdout.write("  ✓ Sample application created for Alice")

        # ── Sample Weekly Log ──────────────────────────────────
        if not WeeklyLog.objects.filter(student=student1).exists():
            WeeklyLog.objects.create(
                student      = student1,
                internship   = created_jobs[1] if created_jobs else None,
                company_name = company_name,
                week_number  = 1,
                hours_worked = 38,
                tasks        = "Set up development environment. Completed onboarding. Reviewed codebase.",
                challenges   = "Understanding the existing Django REST API structure took some time.",
                reflection   = "Great first week. The team is very supportive and I'm already contributing.",
            )
            self.stdout.write("  ✓ Sample weekly log for Alice")

        # ── Sample Notifications ───────────────────────────────
        if not Notification.objects.filter(recipient=student1).exists():
            Notification.objects.create(
                recipient = student1,
                from_name = company_name,
                subject   = "Interview Scheduled — Backend Developer Intern",
                message   = (
                    "Your interview for Backend Developer Intern at TechCorp has been "
                    "scheduled for 15 June 2026 at 10:00 AM via Zoom. "
                    "Please accept or decline in your Student Portal."
                ),
            )
            self.stdout.write("  ✓ Sample notification for Alice")

        # ── Sample Progress Entry ──────────────────────────────
        if not ProgressEntry.objects.filter(student=student1).exists():
            ProgressEntry.objects.create(
                student    = student1,
                internship = created_jobs[1] if created_jobs else None,
                stage      = "Interview",
                notes      = "Interview scheduled for 15 June 2026. Awaiting outcome.",
                set_by     = officer,
            )
            self.stdout.write("  ✓ Sample progress entry for Alice")

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("✅  Demo data seeded successfully!")
        self.stdout.write("")
        self.stdout.write("LOGIN ACCOUNTS:")
        self.stdout.write("  Officer:    officer@iipms.edu.au    / officer123")
        self.stdout.write("  Employer:   hr@techcorp.com.au      / employer123")
        self.stdout.write("  Student 1:  alice@student.edu.au    / student123")
        self.stdout.write("  Student 2:  bob@student.edu.au      / student123")
        self.stdout.write("  Supervisor: supervisor@university.edu.au / super123")
        self.stdout.write("=" * 60)
