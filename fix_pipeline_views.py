content = open('iipms_app/views.py').read()

# ── Fix post_internship view ──
old = '''@login_required
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

    return render(request, "iipms_app/post_internship.html", {"form": form})'''

new = '''@login_required
def post_internship(request):
    if not require_role(request, User.ROLE_EMPLOYER):
        return redirect_to_dashboard(request.user)

    profile, _ = EmployerProfile.objects.get_or_create(
        user=request.user,
        defaults={"company_name": request.user.get_full_name()},
    )

    error = ""
    if request.method == "POST":
        title    = request.POST.get("title",    "").strip()
        location = request.POST.get("location", "").strip()
        skills   = request.POST.get("skills",   "").strip()

        if not title or not location:
            error = "Please fill in the title and location."
        elif not skills:
            error = "Please select at least one required skill."
        else:
            Internship.objects.create(
                employer    = request.user,
                company     = profile.company_name,
                title       = title,
                location    = location,
                duration    = request.POST.get("duration",    ""),
                start_date  = request.POST.get("start_date",  ""),
                end_date    = request.POST.get("end_date",    ""),
                stipend     = request.POST.get("stipend",     ""),
                work_type   = request.POST.get("work_type",   ""),
                industry    = request.POST.get("industry",    ""),
                description = request.POST.get("description", ""),
                skills      = skills,
                is_active   = True,
            )
            messages.success(request, f"Internship posted successfully!")
            return redirect("employer_dashboard")

    return render(request, "iipms_app/post_internship.html", {"error": error})'''

if old in content:
    content = content.replace(old, new)
    print("post_internship view: fixed")
else:
    print("post_internship view: NOT FOUND")

# ── Fix issue_offer view ──
old2 = '''@login_required
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
    })'''

new2 = '''@login_required
def issue_offer(request, app_id):
    if not require_role(request, User.ROLE_EMPLOYER):
        return redirect_to_dashboard(request.user)

    app = get_object_or_404(Application, id=app_id, internship__employer=request.user)

    if request.method == "POST":
        start_date = request.POST.get("start_date", "").strip()
        end_date   = request.POST.get("end_date",   "").strip()
        if not start_date or not end_date:
            messages.error(request, "Please enter start and end dates.")
            return render(request, "iipms_app/issue_offer.html", {"app": app})

        Offer.objects.create(
            employer   = request.user,
            student    = app.student,
            internship = app.internship,
            start_date = start_date,
            end_date   = end_date,
            stipend    = request.POST.get("stipend", ""),
            terms      = request.POST.get("terms",   ""),
        )

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

        messages.success(request, "Offer sent for officer approval!")
        return redirect("employer_dashboard")

    return render(request, "iipms_app/issue_offer.html", {"app": app})'''

if old2 in content:
    content = content.replace(old2, new2)
    print("issue_offer view: fixed")
else:
    print("issue_offer view: NOT FOUND")

# ── Fix submit_evaluation view ──
old3 = '''@login_required
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
    })'''

new3 = '''@login_required
def submit_evaluation(request, student_id, internship_id):
    if not require_role(request, User.ROLE_EMPLOYER, User.ROLE_SUPERVISOR):
        return redirect_to_dashboard(request.user)

    student    = get_object_or_404(User, id=student_id, role=User.ROLE_STUDENT)
    internship = get_object_or_404(Internship, id=internship_id)

    from_role = (
        Evaluation.FROM_EMPLOYER
        if request.user.is_employer()
        else Evaluation.FROM_SUPERVISOR
    )

    RATINGS = [
        ("rating_conduct",       "Professional Conduct"),
        ("rating_technical",     "Technical Ability"),
        ("rating_communication", "Communication Skills"),
        ("rating_overall",       "Overall Performance"),
    ]

    if request.method == "POST":
        Evaluation.objects.create(
            evaluator            = request.user,
            student              = student,
            internship           = internship,
            from_role            = from_role,
            rating_conduct       = int(request.POST.get("rating_conduct",       3)),
            rating_technical     = int(request.POST.get("rating_technical",     3)),
            rating_communication = int(request.POST.get("rating_communication", 3)),
            rating_overall       = int(request.POST.get("rating_overall",       3)),
            comments             = request.POST.get("comments",      ""),
            recommendation       = request.POST.get("recommendation", ""),
        )

        send_notification(
            recipient = student,
            from_name = request.user.get_full_name(),
            subject   = f"New Evaluation — {internship.title}",
            message   = (
                f"An evaluation has been submitted for your internship at "
                f"{internship.company}. View it in your Student Portal."
            ),
        )

        messages.success(request, "Evaluation submitted!")
        return redirect("employer_dashboard")

    return render(request, "iipms_app/submit_evaluation.html", {
        "student":    student,
        "internship": internship,
        "ratings":    RATINGS,
    })'''

if old3 in content:
    content = content.replace(old3, new3)
    print("submit_evaluation view: fixed")
else:
    print("submit_evaluation view: NOT FOUND")

open('iipms_app/views.py', 'w').write(content)
print("\nAll views saved!")
