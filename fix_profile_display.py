import re

# Fix student dashboard
f = 'iipms_app/templates/iipms_app/student_dashboard.html'
txt = open(f).read()

# Replace the JS-powered profile card with Django template tags
old = '''<div class="profile-card">
        <div class="avatar-circle" id="profileAvatar">🎓</div>
        <h2 id="profileName">—</h2>
        <p id="profileEmail" style="font-size:13px;color:#888;"></p>
        <p id="profileCourse" style="font-size:12px;color:#aaa;margin-top:4px;"></p>'''

new = '''<div class="profile-card">
        <div class="avatar-circle" id="profileAvatar">
            {% if user.photo %}
                <img src="{{ user.photo.url }}" alt="Photo">
            {% else %}
                🎓
            {% endif %}
        </div>
        <h2>{{ full_name }}</h2>
        <p style="font-size:13px;color:#888;">{{ email }}</p>
        <p style="font-size:12px;color:#aaa;margin-top:4px;">{{ profile.course }}</p>'''

if old in txt:
    txt = txt.replace(old, new)
    print("profile card fixed")
else:
    print("profile card pattern not found - checking what exists...")
    idx = txt.find('profileName')
    if idx > -1:
        print("Found profileName at:", idx)
        print("Context:", txt[max(0,idx-200):idx+200])

open(f, 'w').write(txt)
