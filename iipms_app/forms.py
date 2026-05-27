# =============================================================
# forms.py
# Django forms define what data the user can submit.
#
# Each form maps to a model (ModelForm) or is standalone.
# Django validates the data automatically based on the rules
# we set here (required fields, max lengths, etc.)
# =============================================================

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User, StudentProfile, EmployerProfile,
    Internship, WeeklyLog, Evaluation, Offer,
)


# -------------------------------------------------------------
# REGISTRATION FORM
# Handles new user sign-up for all four roles.
# -------------------------------------------------------------

class RegisterForm(UserCreationForm):
    """
    Creates a new User account.
    Extends Django's built-in UserCreationForm which already
    handles password hashing and confirmation checks.
    """

    # Fields shown on the form (in addition to password1, password2 from the parent)
    first_name = forms.CharField(max_length=50,  label="First Name",    required=True)
    last_name  = forms.CharField(max_length=50,  label="Last Name",     required=True)
    email      = forms.EmailField(               label="Email Address", required=True)
    role       = forms.ChoiceField(
        choices   = User.ROLE_CHOICES,
        label     = "Register As",
        required  = True,
    )
    photo  = forms.ImageField(label="Profile Photo", required=False)
    phone  = forms.CharField(max_length=20, label="Phone (optional)", required=False)

    # Student-specific
    course        = forms.CharField(max_length=200,           required=False, label="Course / Degree")
    wam           = forms.DecimalField(max_digits=5, decimal_places=2, required=False, label="WAM / GPA")
    availability  = forms.CharField(max_length=100,           required=False, label="Availability")
    industry_pref = forms.ChoiceField(
        choices  = [("", "No preference")] + list(StudentProfile.INDUSTRY_CHOICES),
        required = False,
        label    = "Preferred Industry",
    )
    work_type     = forms.ChoiceField(
        choices  = [("", "No preference")] + list(StudentProfile.WORK_TYPE_CHOICES),
        required = False,
        label    = "Work Type",
    )
    location_pref = forms.CharField(max_length=100, required=False, label="Location Preference")
    skills        = forms.CharField(max_length=500, required=False, label="Your Skills (comma-separated)")
    cv_file       = forms.FileField(required=False, label="Upload CV (optional)")

    # Employer-specific
    company_name = forms.CharField(max_length=200, required=False, label="Company Name")
    emp_industry = forms.CharField(max_length=100, required=False, label="Industry")
    website      = forms.CharField(max_length=200, required=False, label="Company Website")
    abn          = forms.CharField(max_length=20,  required=False, label="ABN")

    # Supervisor-specific
    university  = forms.CharField(max_length=200, required=False, label="University")
    department  = forms.CharField(max_length=200, required=False, label="Department")

    class Meta:
        model  = User
        # We include the standard username field but we'll auto-generate it from email
        fields = ("username", "first_name", "last_name", "email", "role",
                  "password1", "password2", "photo", "phone")

    def clean_email(self):
        """Make sure no two users have the same email."""
        email = self.cleaned_data.get("email", "").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        """
        Save the user, then create the role-specific profile.
        """
        user            = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name  = self.cleaned_data["last_name"]
        user.email      = self.cleaned_data["email"].lower()
        user.role       = self.cleaned_data["role"]
        user.phone      = self.cleaned_data.get("phone", "")

        # Auto-generate a unique username from the email
        # (we use email for login, but Django still needs a username)
        base_username = user.email.split("@")[0]
        username      = base_username
        counter       = 1
        while User.objects.filter(username=username).exists():
            username  = f"{base_username}{counter}"
            counter  += 1
        user.username = username

        if self.cleaned_data.get("photo"):
            user.photo = self.cleaned_data["photo"]

        if commit:
            user.save()

            # Create the role-specific profile
            if user.role == User.ROLE_STUDENT:
                StudentProfile.objects.create(
                    user          = user,
                    course        = self.cleaned_data.get("course",        ""),
                    wam           = self.cleaned_data.get("wam"),
                    availability  = self.cleaned_data.get("availability",  ""),
                    industry_pref = self.cleaned_data.get("industry_pref", ""),
                    work_type     = self.cleaned_data.get("work_type",     ""),
                    location_pref = self.cleaned_data.get("location_pref", ""),
                    skills        = self.cleaned_data.get("skills",        ""),
                    cv_file       = self.cleaned_data.get("cv_file"),
                )

            elif user.role == User.ROLE_EMPLOYER:
                EmployerProfile.objects.create(
                    user         = user,
                    company_name = self.cleaned_data.get("company_name", user.get_full_name()),
                    industry     = self.cleaned_data.get("emp_industry", ""),
                    website      = self.cleaned_data.get("website",      ""),
                    abn          = self.cleaned_data.get("abn",          ""),
                )

            elif user.role == User.ROLE_SUPERVISOR:
                from .models import SupervisorProfile
                SupervisorProfile.objects.create(
                    user       = user,
                    university = self.cleaned_data.get("university", ""),
                    department = self.cleaned_data.get("department", ""),
                )

        return user


# -------------------------------------------------------------
# STUDENT PROFILE EDIT FORM
# -------------------------------------------------------------

class StudentProfileForm(forms.ModelForm):
    """Lets a student update their profile details and skills."""

    class Meta:
        model  = StudentProfile
        fields = [
            "course", "wam", "availability",
            "skills", "industry_pref", "work_type", "location_pref",
            "cv_file",
        ]
        labels = {
            "course":        "Course / Degree",
            "wam":           "WAM / GPA",
            "availability":  "Availability (when can you start?)",
            "skills":        "Your Skills (comma-separated, e.g. Python, SQL, React)",
            "industry_pref": "Preferred Industry",
            "work_type":     "Work Type Preference",
            "location_pref": "Location Preference",
            "cv_file":       "Upload / Replace CV",
        }
        widgets = {
            "skills": forms.TextInput(attrs={
                "placeholder": "e.g. Python, SQL, Django, Excel",
            }),
        }


# -------------------------------------------------------------
# EMPLOYER PROFILE FORM
# -------------------------------------------------------------

class EmployerProfileForm(forms.ModelForm):
    """Lets an employer update their company details."""

    class Meta:
        model  = EmployerProfile
        fields = ["company_name", "industry", "website", "abn"]


# -------------------------------------------------------------
# INTERNSHIP POSTING FORM
# -------------------------------------------------------------

class InternshipForm(forms.ModelForm):
    """Employer uses this to create a new internship listing."""

    class Meta:
        model  = Internship
        fields = [
            "title", "location", "duration", "description",
            "skills", "stipend", "industry", "work_type",
            "start_date", "end_date",
        ]
        labels = {
            "title":       "Internship Title *",
            "location":    "Location *",
            "duration":    "Duration (e.g. 3 months)",
            "description": "Description",
            "skills":      "Required Skills (comma-separated) *",
            "stipend":     "Stipend (optional)",
            "industry":    "Industry",
            "work_type":   "Work Type",
            "start_date":  "Start Date",
            "end_date":    "End Date",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "skills":      forms.TextInput(attrs={"placeholder": "e.g. Python, SQL, Excel"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Please enter a title.")
        return title

    def clean_skills(self):
        skills = self.cleaned_data.get("skills", "").strip()
        if not skills:
            raise forms.ValidationError("Please enter at least one required skill.")
        return skills


# -------------------------------------------------------------
# WEEKLY LOG FORM
# -------------------------------------------------------------

class WeeklyLogForm(forms.ModelForm):
    """Student submits their weekly progress report."""

    class Meta:
        model  = WeeklyLog
        fields = ["company_name", "week_number", "hours_worked", "tasks", "challenges", "reflection"]
        labels = {
            "company_name": "Company / Employer",
            "week_number":  "Week Number",
            "hours_worked": "Hours Worked",
            "tasks":        "Tasks Completed",
            "challenges":   "Challenges Faced (optional)",
            "reflection":   "Weekly Reflection",
        }
        widgets = {
            "tasks":       forms.Textarea(attrs={"rows": 4, "placeholder": "Describe what you worked on..."}),
            "challenges":  forms.Textarea(attrs={"rows": 3, "placeholder": "Any blockers or difficulties?"}),
            "reflection":  forms.Textarea(attrs={"rows": 4, "placeholder": "What did you learn this week?"}),
        }


# -------------------------------------------------------------
# EVALUATION FORM
# -------------------------------------------------------------

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 to 5

class EvaluationForm(forms.ModelForm):
    """
    Employer or supervisor submits a performance evaluation for a student.
    """

    rating_conduct       = forms.ChoiceField(choices=RATING_CHOICES, label="Professional Conduct (1-5)")
    rating_technical     = forms.ChoiceField(choices=RATING_CHOICES, label="Technical Ability (1-5)")
    rating_communication = forms.ChoiceField(choices=RATING_CHOICES, label="Communication (1-5)")
    rating_overall       = forms.ChoiceField(choices=RATING_CHOICES, label="Overall Performance (1-5)")

    class Meta:
        model  = Evaluation
        fields = [
            "rating_conduct", "rating_technical",
            "rating_communication", "rating_overall",
            "comments", "recommendation",
        ]
        labels = {
            "comments":       "Comments",
            "recommendation": "Recommendation (e.g. Hire Again, Good, Needs Improvement)",
        }
        widgets = {
            "comments": forms.Textarea(attrs={"rows": 4}),
        }


# -------------------------------------------------------------
# OFFER FORM
# -------------------------------------------------------------

class OfferForm(forms.ModelForm):
    """Employer issues a formal offer letter to a student."""

    class Meta:
        model  = Offer
        fields = ["start_date", "end_date", "stipend", "terms"]
        labels = {
            "start_date": "Start Date",
            "end_date":   "End Date",
            "stipend":    "Stipend / Pay",
            "terms":      "Terms and Conditions",
        }
        widgets = {
            "terms": forms.Textarea(attrs={"rows": 4}),
        }
