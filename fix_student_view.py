content = open('iipms_app/views.py').read()

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
        "user":         user,
        "full_name":    user.get_full_name(),
        "email":        user.email,
    }
    return render(request, "iipms_app/student_dashboard.html", context)'''

new = '''    # Build internships with match scores for the browse tab
    from .matching import rank_internships_for_student
    ranked = rank_internships_for_student(profile, internships)
    internships_with_scores = []
    for r in ranked:
        colour = "green" if r["score"] >= 70 else "orange" if r["score"] >= 40 else "red"
        internships_with_scores.append({
            "job":           r["internship"],
            "score":         r["score"],
            "bar_colour":    colour,
            "already_applied": r["internship"].id in list(applied_ids),
        })

    context = {
        "profile":                profile,
        "applications":           applications,
        "notifications":          notifications,
        "offers":                 offers,
        "evaluations":            evaluations,
        "logs":                   logs,
        "unread_count":           unread_count,
        "internships":            internships,
        "internships_with_scores": internships_with_scores,
        "applied_ids":            list(applied_ids),
        "user":                   user,
        "full_name":              user.get_full_name(),
        "email":                  user.email,
    }
    return render(request, "iipms_app/student_dashboard.html", context)'''

if old in content:
    content = content.replace(old, new)
    open('iipms_app/views.py', 'w').write(content)
    print("student view fixed")
else:
    print("NOT FOUND - searching...")
    idx = content.find('"internships":  internships,')
    print("Found internships at index:", idx)
    print("Context:", content[idx-100:idx+200])
