content = open('iipms_app/views.py').read()

old = '''@login_required
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
    })'''

new = '''@login_required
def student_profile_edit(request):
    if not require_role(request, User.ROLE_STUDENT):
        return redirect_to_dashboard(request.user)

    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    ALL_SKILLS = {
        "programming": ["Python","JavaScript","Java","C++","C#","TypeScript","Swift","Kotlin","Go","Rust","PHP","Ruby","R","MATLAB"],
        "web":         ["HTML","CSS","React","Vue.js","Angular","Node.js","Django","Flask","Laravel","Next.js","Bootstrap","Tailwind CSS"],
        "data":        ["SQL","MySQL","PostgreSQL","MongoDB","Machine Learning","Deep Learning","TensorFlow","PyTorch","Pandas","NumPy","Tableau","Power BI","Excel"],
        "cloud":       ["AWS","Azure","Google Cloud","Docker","Kubernetes","Git","GitHub","CI/CD","Linux"],
        "other":       ["React Native","Flutter","Android Development","iOS Development","Figma","UI/UX Design","Agile","Scrum","REST APIs","GraphQL","Cybersecurity","Networking"],
    }

    current_skills = [s.strip() for s in profile.skills.split(",") if s.strip()]

    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", request.user.first_name)
        request.user.last_name  = request.POST.get("last_name",  request.user.last_name)
        if request.FILES.get("photo"):
            request.user.photo = request.FILES["photo"]
        request.user.save()

        wam_val = None
        try:
            wam_raw = request.POST.get("wam", "")
            if wam_raw:
                wam_val = float(wam_raw)
        except ValueError:
            pass

        profile.course        = request.POST.get("course",        "")
        profile.wam           = wam_val
        profile.availability  = request.POST.get("availability",  "")
        profile.skills        = request.POST.get("skills",        "")
        profile.industry_pref = request.POST.get("industry_pref", "")
        profile.work_type     = request.POST.get("work_type",     "")
        profile.location_pref = request.POST.get("location_pref", "")
        if request.FILES.get("cv_file"):
            profile.cv_file = request.FILES["cv_file"]
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("student_dashboard")

    return render(request, "iipms_app/student_profile_edit.html", {
        "profile":         profile,
        "all_skills":      ALL_SKILLS,
        "current_skills":  current_skills,
        "industry_choices": StudentProfile.INDUSTRY_CHOICES,
    })'''

if old in content:
    content = content.replace(old, new)
    open('iipms_app/views.py', 'w').write(content)
    print("student_profile_edit fixed")
else:
    print("NOT FOUND")
