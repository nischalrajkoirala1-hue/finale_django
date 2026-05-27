with open('iipms_app/views.py', 'r') as f:
    content = f.read()

# Fix employer dashboard context
old = '''    context = {
        "profile":      profile,
        "my_jobs":      my_jobs,
        "applications": applications,
        "hired_count":  hired_count,
        "my_logs":      my_logs,
    }
    return render(request, "iipms_app/employer_dashboard.html", context)'''

new = '''    context = {
        "profile":      profile,
        "my_jobs":      my_jobs,
        "applications": applications,
        "hired_count":  hired_count,
        "my_logs":      my_logs,
        "user":         request.user,
        "full_name":    request.user.get_full_name(),
        "email":        request.user.email,
        "company_name": profile.company_name,
        "industry":     profile.industry,
        "website":      profile.website,
        "abn":          profile.abn,
    }
    return render(request, "iipms_app/employer_dashboard.html", context)'''

content = content.replace(old, new)
open('iipms_app/views.py', 'w').write(content)
print("employer context fixed")
