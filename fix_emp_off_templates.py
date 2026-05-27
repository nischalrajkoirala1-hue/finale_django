import re

# Fix employer dashboard template
f = 'iipms_app/templates/iipms_app/employer_dashboard.html'
txt = open(f).read()

# Replace JS profile display with Django tags
txt = re.sub(
    r'<h2 id="empName">[^<]*</h2>',
    '<h2>{{ full_name }}</h2>',
    txt
)
txt = re.sub(
    r'<p id="empEmail"[^>]*>[^<]*</p>',
    '<p style="font-size:13px;color:#888;">{{ email }}</p>',
    txt
)
txt = re.sub(
    r'<p id="empCompany"[^>]*>[^<]*</p>',
    '<p style="font-size:12px;color:#aaa;margin-top:4px;">{{ company_name }}</p>',
    txt
)
txt = re.sub(
    r'<p id="empIndustry"[^>]*>[^<]*</p>',
    '<p style="font-size:12px;color:#aaa;">{{ industry }}</p>',
    txt
)

open(f, 'w').write(txt)
print("employer template fixed")

# Fix officer dashboard template
f2 = 'iipms_app/templates/iipms_app/officer_dashboard.html'
txt2 = open(f2).read()

txt2 = re.sub(
    r'<h2 id="officerName">[^<]*</h2>',
    '<h2>{{ full_name }}</h2>',
    txt2
)
txt2 = re.sub(
    r'<p id="officerEmail"[^>]*>[^<]*</p>',
    '<p style="font-size:13px;color:#888;">{{ email }}</p>',
    txt2
)

open(f2, 'w').write(txt2)
print("officer template fixed")
