content = open('iipms_app/views.py').read()

old = '''def register_view(request):
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

    return render(request, "iipms_app/register.html", {"form": form})'''

new = '''def register_view(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)

    error = ""

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name  = request.POST.get("last_name",  "").strip()
        email      = request.POST.get("email",      "").strip().lower()
        role       = request.POST.get("role",       "").strip()
        password1  = request.POST.get("password1",  "")
        password2  = request.POST.get("password2",  "")

        if not first_name or not last_name or not email or not role or not password1:
            error = "Please fill in all required fields."
        elif password1 != password2:
            error = "Passwords do not match."
        elif len(password1) < 6:
            error = "Password must be at least 6 characters."
        elif User.objects.filter(email=email).exists():
            error = "An account with this email already exists."
        else:
            base_username = email.split("@")[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User(
                username   = username,
                first_name = first_name,
                last_name  = last_name,
                email      = email,
                role       = role,
            )
            user.set_password(password1)
            if request.FILES.get("photo"):
                user.photo = request.FILES["photo"]
            user.save()

            if role == "student":
                wam_val = None
                try:
                    wam_raw = request.POST.get("wam", "")
                    if wam_raw:
                        wam_val = float(wam_raw)
                except ValueError:
                    pass
                StudentProfile.objects.create(
                    user          = user,
                    course        = request.POST.get("course",        ""),
                    wam           = wam_val,
                    availability  = request.POST.get("availability",  ""),
                    industry_pref = request.POST.get("industry_pref", ""),
                    work_type     = request.POST.get("work_type",     ""),
                    location_pref = request.POST.get("location_pref", ""),
                    skills        = request.POST.get("skills",        ""),
                    cv_file       = request.FILES.get("cv_file"),
                )
            elif role == "employer":
                EmployerProfile.objects.create(
                    user         = user,
                    company_name = request.POST.get("company_name", first_name),
                    industry     = request.POST.get("emp_industry", ""),
                    website      = request.POST.get("website",      ""),
                    abn          = request.POST.get("abn",          ""),
                )
            elif role == "supervisor":
                SupervisorProfile.objects.create(
                    user       = user,
                    university = request.POST.get("university", ""),
                    department = request.POST.get("department", ""),
                )

            login(request, user)
            return redirect_to_dashboard(user)

    return render(request, "iipms_app/register.html", {"error": error})'''

if old in content:
    content = content.replace(old, new)
    open('iipms_app/views.py', 'w').write(content)
    print("SUCCESS - register view updated")
else:
    print("NOT FOUND - searching for register_view...")
    idx = content.find("def register_view")
    print("Found at index:", idx)
    print("Context:", content[idx:idx+200])
