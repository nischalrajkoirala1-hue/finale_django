with open('iipms_app/views.py', 'r') as f:
    content = f.read()

# Fix officer dashboard context
old = '''    context = {
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
    return render(request, "iipms_app/officer_dashboard.html", context)'''

new = '''    context = {
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
        "user":              request.user,
        "full_name":         request.user.get_full_name(),
        "email":             request.user.email,
    }
    return render(request, "iipms_app/officer_dashboard.html", context)'''

content = content.replace(old, new)
open('iipms_app/views.py', 'w').write(content)
print("officer context fixed")
