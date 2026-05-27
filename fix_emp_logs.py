content = open('iipms_app/views.py').read()

old = '    my_logs        = WeeklyLog.objects.filter(company_name__iexact=profile.company_name)'
new = '    my_logs        = WeeklyLog.objects.filter(internship__employer=request.user).order_by("-submitted_at")'

if old in content:
    content = content.replace(old, new)
    print("logs query fixed")
else:
    print("logs query not found - trying alternative")
    content = content.replace(
        'WeeklyLog.objects.filter(company_name__iexact=profile.company_name)',
        'WeeklyLog.objects.filter(internship__employer=request.user).order_by("-submitted_at")'
    )

open('iipms_app/views.py', 'w').write(content)
print("done")
