with open('iipms_app/views.py', 'r') as f:
    content = f.read()

# Fix student dashboard to pass user data to template
old = '''    context = {
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
    return render(request, "iipms_app/student_dashboard.html", context)'''

new = '''    context = {
        "profile":      profile,
        "applications": applications,
        "notifications": notifications,
        "offers":       offers,
        "evaluations":  evaluations,
        "logs":         logs,
        "unread_count": unread_count,
        "internships":  internships,
        "applied_ids":  list(applied_ids),
        "user":         user,
        "full_name":    user.get_full_name(),
        "email":        user.email,
    }
    return render(request, "iipms_app/student_dashboard.html", context)'''

content = content.replace(old, new)
open('iipms_app/views.py', 'w').write(content)
print("done")
