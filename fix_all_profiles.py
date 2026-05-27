import re

# ── STUDENT DASHBOARD ──
f = 'iipms_app/templates/iipms_app/student_dashboard.html'
txt = open(f).read()

# Fix skills display
old1 = '''        <div style="margin-top:10px;">
            <strong style="font-size:13px;">My Skills:</strong>
            <div id="skillBadges" style="margin-top:6px;"></div>
        </div>
        <button onclick="openSkillPopup()" style="margin-top:12px;padding:7px 16px;background:#4f6ef7;color:white;border:none;border-radius:8px;cursor:pointer;font-size:13px;">✏️ Edit Skills</button>'''

new1 = '''        <div style="margin-top:10px;">
            <strong style="font-size:13px;">My Skills:</strong>
            <div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">
                {% if profile.skills %}
                    {% for skill in profile.skills.split %}
                    <span style="background:#e8ecff;color:#4f6ef7;padding:2px 8px;border-radius:10px;font-size:11px;">{{ skill }}</span>
                    {% endfor %}
                {% else %}
                    <span style="font-size:12px;color:#aaa;">No skills added yet</span>
                {% endif %}
            </div>
        </div>
        <a href="/student/profile/edit/" style="display:block;margin-top:12px;padding:7px 16px;background:#4f6ef7;color:white;border-radius:8px;font-size:13px;text-align:center;text-decoration:none;">✏️ Edit Profile</a>'''

if old1 in txt:
    txt = txt.replace(old1, new1)
    print("student skills: fixed")
else:
    print("student skills: pattern not found, trying regex")
    txt = re.sub(
        r'<div id="skillBadges"[^>]*></div>',
        '''<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;">{% if profile.skills %}{% for skill in profile.skills.split %}<span style="background:#e8ecff;color:#4f6ef7;padding:2px 8px;border-radius:10px;font-size:11px;">{{ skill }}</span>{% endfor %}{% else %}<span style="font-size:12px;color:#aaa;">No skills added</span>{% endif %}</div>''',
        txt
    )
    txt = re.sub(
        r'<button onclick="openSkillPopup\(\)"[^>]*>✏️ Edit Skills</button>',
        '<a href="/student/profile/edit/" style="display:block;margin-top:12px;padding:7px 16px;background:#4f6ef7;color:white;border-radius:8px;font-size:13px;text-align:center;text-decoration:none;">✏️ Edit Profile</a>',
        txt
    )
    print("student skills: regex applied")

# Fix stats
txt = re.sub(r'<h3 id="statApps">0</h3>', '<h3>{{ applications.count }}</h3>', txt)
txt = re.sub(r'<h3 id="statNotifs">0</h3>', '<h3>{{ unread_count }}</h3>', txt)
txt = re.sub(r'<h3 id="statLogs">0</h3>', '<h3>{{ logs.count }}</h3>', txt)
print("student stats: fixed")

open(f, 'w').write(txt)
print("student dashboard saved")

# ── EMPLOYER DASHBOARD ──
f2 = 'iipms_app/templates/iipms_app/employer_dashboard.html'
txt2 = open(f2).read()

# Replace entire profile card with Django data
old_emp = re.search(r'<div class="profile-card">.*?</div>\s*\n\s*<div class="dashboard-content">', txt2, re.DOTALL)
if old_emp:
    new_emp_card = '''<div class="profile-card">
        <div class="avatar-circle">
            {% if user.photo %}
                <img src="{{ user.photo.url }}" alt="Photo">
            {% else %}
                🏢
            {% endif %}
        </div>
        <h2>{{ full_name }}</h2>
        <p style="font-size:13px;color:#888;">{{ email }}</p>
        <p style="font-size:13px;color:#555;margin-top:6px;font-weight:bold;">{{ company_name }}</p>
        <p style="font-size:12px;color:#aaa;">{{ industry }}</p>
        {% if website %}
        <p style="font-size:12px;color:#4f6ef7;margin-top:4px;">🌐 {{ website }}</p>
        {% endif %}
        {% if abn %}
        <p style="font-size:12px;color:#aaa;">ABN: {{ abn }}</p>
        {% endif %}
        <div style="margin-top:10px;padding:8px;background:#f8faff;border-radius:8px;font-size:12px;">
            <p>📋 <strong>{{ my_jobs.count }}</strong> Internships Posted</p>
            <p>👥 <strong>{{ applications.count }}</strong> Applications Received</p>
            <p>✅ <strong>{{ hired_count }}</strong> Hired</p>
        </div>
    </div>

    <div class="dashboard-content">'''
    txt2 = txt2[:old_emp.start()] + new_emp_card + txt2[old_emp.end():]
    print("employer profile card: fixed")
else:
    # Try simpler replacement
    txt2 = re.sub(r'<h2 id="empName">[^<]*</h2>', '<h2>{{ full_name }}</h2>', txt2)
    txt2 = re.sub(r'<p id="empEmail"[^>]*>[^<]*</p>', '<p style="font-size:13px;color:#888;">{{ email }}</p>', txt2)
    txt2 = re.sub(r'<p id="empCompany"[^>]*>[^<]*</p>', '<p style="font-size:13px;color:#555;font-weight:bold;">{{ company_name }}</p>', txt2)
    txt2 = re.sub(r'<p id="empIndustry"[^>]*>[^<]*</p>', '<p style="font-size:12px;color:#aaa;">{{ industry }}</p>', txt2)
    print("employer profile: regex applied")

# Fix employer stats
txt2 = re.sub(r'<h3 id="statJobs">0</h3>', '<h3>{{ my_jobs.count }}</h3>', txt2)
txt2 = re.sub(r'<h3 id="statApps">0</h3>', '<h3>{{ applications.count }}</h3>', txt2)
txt2 = re.sub(r'<h3 id="statHired">0</h3>', '<h3>{{ hired_count }}</h3>', txt2)
print("employer stats: fixed")

open(f2, 'w').write(txt2)
print("employer dashboard saved")

# ── OFFICER DASHBOARD ──
f3 = 'iipms_app/templates/iipms_app/officer_dashboard.html'
txt3 = open(f3).read()

txt3 = re.sub(r'<h2 id="officerName">[^<]*</h2>', '<h2>{{ full_name }}</h2>', txt3)
txt3 = re.sub(r'<p id="officerEmail"[^>]*>[^<]*</p>', '<p style="font-size:13px;color:#888;">{{ email }}</p>', txt3)
txt3 = re.sub(r'<h3 id="statStudents">0</h3>', '<h3>{{ student_count }}</h3>', txt3)
txt3 = re.sub(r'<h3 id="statInternships">0</h3>', '<h3>{{ internship_count }}</h3>', txt3)
txt3 = re.sub(r'<h3 id="statApplications">0</h3>', '<h3>{{ application_count }}</h3>', txt3)
txt3 = re.sub(r'<h3 id="statPlaced">0</h3>', '<h3>{{ placed_count }}</h3>', txt3)

# Add profile card if missing
if 'profile-card' not in txt3:
    profile_card = '''<div class="profile-card">
        <div class="avatar-circle">
            {% if user.photo %}
                <img src="{{ user.photo.url }}" alt="Photo">
            {% else %}
                👩‍💼
            {% endif %}
        </div>
        <h2>{{ full_name }}</h2>
        <p style="font-size:13px;color:#888;">{{ email }}</p>
        <p style="font-size:12px;color:#aaa;margin-top:4px;">Placement Officer</p>
        <div style="margin-top:10px;padding:8px;background:#f8faff;border-radius:8px;font-size:12px;">
            <p>🎓 <strong>{{ student_count }}</strong> Students</p>
            <p>💼 <strong>{{ internship_count }}</strong> Internships</p>
            <p>📋 <strong>{{ application_count }}</strong> Applications</p>
            <p>✅ <strong>{{ placed_count }}</strong> Placed</p>
        </div>
    </div>'''
    txt3 = txt3.replace('<div class="dashboard-content">', profile_card + '\n    <div class="dashboard-content">', 1)
    print("officer profile card: added")
else:
    print("officer profile: updated existing")

print("officer stats: fixed")
open(f3, 'w').write(txt3)
print("officer dashboard saved")

print("\nAll done!")
