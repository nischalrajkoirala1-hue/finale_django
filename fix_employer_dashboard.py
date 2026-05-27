import re

f = 'iipms_app/templates/iipms_app/employer_dashboard.html'
txt = open(f).read()

# Find the applications tab section and replace with full pipeline UI
# First check what tab structure exists
if 'tab-panel' in txt or 'showTab' in txt:
    print("Tab structure found - patching applications section")
else:
    print("No tab structure - will inject full dashboard")

# Replace the entire dashboard content with a proper version
new_dashboard = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Employer Dashboard - IIPMS</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    <style>
        .tab-btn{padding:9px 18px;background:#f1f5f9;border:none;border-radius:8px;cursor:pointer;font-size:13px;margin-right:6px;margin-bottom:8px;}
        .tab-btn.active{background:#4f6ef7;color:white;}
        .tab-panel{display:none;}
        .tab-panel.active{display:block;}
        .card{background:white;padding:15px;border-radius:8px;margin-bottom:12px;box-shadow:0 2px 6px rgba(0,0,0,0.08);}
        .badge{display:inline-block;padding:3px 10px;border-radius:10px;font-size:12px;font-weight:bold;}
        .badge-pending{background:#fef9c3;color:#a16207;}
        .badge-review{background:#dbeafe;color:#1d4ed8;}
        .badge-interview{background:#e0e7ff;color:#4338ca;}
        .badge-offer{background:#fce7f3;color:#be185d;}
        .badge-hired{background:#dcfce7;color:#15803d;}
        .badge-rejected{background:#fee2e2;color:#b91c1c;}
        .action-select{padding:6px 10px;border:1.5px solid #4f6ef7;border-radius:6px;font-size:13px;color:#4f6ef7;background:white;cursor:pointer;}
        .btn-primary{padding:7px 14px;background:#4f6ef7;color:white;border:none;border-radius:6px;cursor:pointer;font-size:13px;text-decoration:none;display:inline-block;}
        .btn-success{padding:7px 14px;background:#22c55e;color:white;border:none;border-radius:6px;cursor:pointer;font-size:13px;text-decoration:none;display:inline-block;}
        .btn-danger{padding:7px 14px;background:#ef4444;color:white;border:none;border-radius:6px;cursor:pointer;font-size:13px;}
        .modal-bg{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:999;justify-content:center;align-items:center;}
        .modal-bg.show{display:flex;}
        .modal-box{background:white;border-radius:12px;padding:28px;max-width:480px;width:90%;}
        input,textarea,select{width:100%;padding:10px 14px;border:1px solid #cbd5e1;border-radius:6px;font-size:14px;outline:none;font-family:Arial,sans-serif;box-sizing:border-box;}
        textarea{resize:vertical;}
    </style>
</head>
<body>

<header class="navbar">
    <div class="logo">IIPMS</div>
    <nav><ul>
        <li><a href="/employer/">Dashboard</a></li>
        <li><a href="/employer/post/" class="btn">+ Post Internship</a></li>
        <li><a href="/logout/">Logout</a></li>
    </ul></nav>
</header>

<!-- Django messages -->
{% if messages %}
<div style="position:fixed;top:70px;right:20px;z-index:9999;width:320px;">
    {% for message in messages %}
    <div style="background:{% if message.tags == 'success' %}#dcfce7{% else %}#fee2e2{% endif %};border-radius:8px;padding:12px 16px;margin-bottom:8px;color:{% if message.tags == 'success' %}#15803d{% else %}#b91c1c{% endif %};font-size:14px;font-weight:bold;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        {{ message }}
    </div>
    {% endfor %}
</div>
{% endif %}

<div class="dashboard">

    <!-- Profile Card -->
    <div class="profile-card">
        <div class="avatar-circle">
            {% if user.photo %}<img src="{{ user.photo.url }}" alt="Photo">{% else %}🏢{% endif %}
        </div>
        <h2>{{ full_name }}</h2>
        <p style="font-size:13px;color:#888;">{{ email }}</p>
        <p style="font-size:13px;font-weight:bold;color:#1e293b;margin-top:6px;">{{ company_name }}</p>
        <p style="font-size:12px;color:#aaa;">{{ industry }}</p>
        {% if website %}<p style="font-size:12px;color:#4f6ef7;">🌐 {{ website }}</p>{% endif %}
        {% if abn %}<p style="font-size:12px;color:#aaa;">ABN: {{ abn }}</p>{% endif %}

        <div style="margin-top:12px;padding:10px;background:#f8faff;border-radius:8px;font-size:13px;">
            <p>📋 <strong>{{ my_jobs.count }}</strong> Jobs Posted</p>
            <p>👥 <strong>{{ applications.count }}</strong> Applications</p>
            <p>✅ <strong>{{ hired_count }}</strong> Hired</p>
        </div>

        <a href="/employer/post/" style="display:block;margin-top:12px;padding:8px;background:#4f6ef7;color:white;border-radius:8px;text-align:center;text-decoration:none;font-size:13px;">+ Post New Internship</a>
    </div>

    <!-- Dashboard Content -->
    <div class="dashboard-content">

        <!-- Stats -->
        <div class="stats">
            <div class="stat-box"><h3>{{ my_jobs.count }}</h3><p>Jobs Posted</p></div>
            <div class="stat-box"><h3>{{ applications.count }}</h3><p>Applications</p></div>
            <div class="stat-box"><h3>{{ hired_count }}</h3><p>Hired</p></div>
        </div>

        <!-- Tabs -->
        <div style="margin-top:18px;">
            <button class="tab-btn active" onclick="showTab('jobs',this)">💼 My Internships</button>
            <button class="tab-btn" onclick="showTab('applications',this)">📋 Applications</button>
            <button class="tab-btn" onclick="showTab('logs',this)">📝 Intern Logs</button>
        </div>

        <!-- TAB 1: MY JOBS -->
        <div class="tab-panel active" id="tab-jobs">
            <h3 style="margin:16px 0 12px;">Your Posted Internships</h3>
            {% if my_jobs %}
                {% for job in my_jobs %}
                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <p style="font-weight:bold;font-size:15px;margin:0 0 4px;">{{ job.title }}</p>
                            <p style="font-size:13px;color:#555;">📍 {{ job.location }} {% if job.duration %}| ⏱ {{ job.duration }}{% endif %} {% if job.stipend %}| 💰 {{ job.stipend }}{% endif %}</p>
                            <p style="font-size:13px;color:#555;">🎯 {{ job.skills }}</p>
                            {% if job.description %}<p style="font-size:13px;color:#666;margin-top:4px;">{{ job.description }}</p>{% endif %}
                        </div>
                        <div style="text-align:right;flex-shrink:0;padding-left:12px;">
                            {% if job.is_active %}
                                <span class="badge" style="background:#dcfce7;color:#15803d;">✓ Active</span>
                            {% else %}
                                <span class="badge" style="background:#f1f5f9;color:#888;">Closed</span>
                            {% endif %}
                            <p style="font-size:12px;color:#aaa;margin-top:4px;">
                                {{ job.applications.count }} application{{ job.applications.count|pluralize }}
                            </p>
                        </div>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div style="text-align:center;padding:40px;color:#aaa;">
                    <p style="font-size:15px;">No internships posted yet.</p>
                    <a href="/employer/post/" class="btn-primary" style="margin-top:12px;">Post Your First Internship</a>
                </div>
            {% endif %}
        </div>

        <!-- TAB 2: APPLICATIONS & HIRING PIPELINE -->
        <div class="tab-panel" id="tab-applications">
            <h3 style="margin:16px 0 12px;">Applications & Hiring Pipeline</h3>
            {% if applications %}
                {% for app in applications %}
                <div class="card" style="border-left:4px solid
                    {% if app.status == 'Hired' %}#22c55e
                    {% elif app.status == 'Rejected' %}#ef4444
                    {% elif app.status == 'Interview Scheduled' %}#6366f1
                    {% elif app.status == 'Offer Extended' %}#ec4899
                    {% else %}#4f6ef7{% endif %};">

                    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;">
                        <div>
                            <p style="font-weight:bold;font-size:15px;margin:0 0 3px;">{{ app.student.get_full_name }}</p>
                            <p style="font-size:13px;color:#555;">📧 {{ app.student.email }}</p>
                            <p style="font-size:13px;color:#555;">💼 {{ app.internship.title }}</p>
                            {% if app.skills_at_apply %}
                            <p style="font-size:12px;color:#777;margin-top:3px;">🎯 Skills: {{ app.skills_at_apply }}</p>
                            {% endif %}
                            {% if app.student_response %}
                            <p style="font-size:12px;color:#4f6ef7;margin-top:3px;">↩ Student response: {{ app.student_response }}</p>
                            {% endif %}
                            <p style="font-size:11px;color:#aaa;margin-top:4px;">Applied: {{ app.applied_at|date:"d M Y" }}</p>
                        </div>
                        <div style="text-align:right;">
                            <span class="badge badge-{% if app.status == 'Hired' %}hired{% elif app.status == 'Rejected' %}rejected{% elif app.status == 'Interview Scheduled' %}interview{% elif app.status == 'Offer Extended' %}offer{% elif app.status == 'Under Review' %}review{% else %}pending{% endif %}">
                                {{ app.status }}
                            </span>
                        </div>
                    </div>

                    <!-- Action buttons based on current status -->
                    <div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;">

                        {% if app.status == 'Pending' or app.status == 'Under Review' %}
                            <!-- Move to review or schedule interview -->
                            <form method="POST" action="/employer/application/{{ app.id }}/status/" style="margin:0;">
                                {% csrf_token %}
                                <input type="hidden" name="status" value="Under Review">
                                <button type="submit" class="btn-primary">👁 Mark Under Review</button>
                            </form>
                            <button onclick="openInterviewModal({{ app.id }})" class="btn-primary" style="background:#6366f1;">📅 Schedule Interview</button>
                            <form method="POST" action="/employer/application/{{ app.id }}/status/" style="margin:0;">
                                {% csrf_token %}
                                <input type="hidden" name="status" value="Rejected">
                                <button type="submit" class="btn-danger" onclick="return confirm('Reject this application?')">✗ Reject</button>
                            </form>

                        {% elif app.status == 'Interview Scheduled' %}
                            {% if app.interview_date %}
                            <span style="font-size:13px;color:#6366f1;">📅 Interview: {{ app.interview_date }}</span>
                            {% endif %}
                            {% if app.student_response == 'Accepted Interview' %}
                                <!-- Student accepted interview - can now shortlist or hire -->
                                <form method="POST" action="/employer/application/{{ app.id }}/status/" style="margin:0;">
                                    {% csrf_token %}
                                    <input type="hidden" name="status" value="Shortlisted">
                                    <button type="submit" class="btn-primary">⭐ Shortlist</button>
                                </form>
                                <a href="/employer/offer/{{ app.id }}/" class="btn-success">📄 Issue Offer</a>
                                <form method="POST" action="/employer/application/{{ app.id }}/status/" style="margin:0;">
                                    {% csrf_token %}
                                    <input type="hidden" name="status" value="Rejected">
                                    <button type="submit" class="btn-danger" onclick="return confirm('Reject?')">✗ Reject</button>
                                </form>
                            {% elif app.student_response == 'Declined Interview' %}
                                <span style="color:#ef4444;font-size:13px;">Student declined interview</span>
                                <form method="POST" action="/employer/application/{{ app.id }}/status/" style="margin:0;">
                                    {% csrf_token %}
                                    <input type="hidden" name="status" value="Rejected">
                                    <button type="submit" class="btn-danger">✗ Close Application</button>
                                </form>
                            {% else %}
                                <span style="font-size:13px;color:#aaa;">⏳ Awaiting student response...</span>
                                <a href="/employer/offer/{{ app.id }}/" class="btn-success">📄 Issue Offer Anyway</a>
                            {% endif %}

                        {% elif app.status == 'Shortlisted' or app.status == 'Reference Check' %}
                            <a href="/employer/offer/{{ app.id }}/" class="btn-success">📄 Issue Offer Letter</a>
                            <form method="POST" action="/employer/application/{{ app.id }}/status/" style="margin:0;">
                                {% csrf_token %}
                                <input type="hidden" name="status" value="Reference Check">
                                <button type="submit" class="btn-primary">🔍 Reference Check</button>
                            </form>
                            <form method="POST" action="/employer/application/{{ app.id }}/status/" style="margin:0;">
                                {% csrf_token %}
                                <input type="hidden" name="status" value="Rejected">
                                <button type="submit" class="btn-danger" onclick="return confirm('Reject?')">✗ Reject</button>
                            </form>

                        {% elif app.status == 'Offer Extended' %}
                            {% if app.student_response == 'Accepted Offer' %}
                                <form method="POST" action="/employer/application/{{ app.id }}/status/" style="margin:0;">
                                    {% csrf_token %}
                                    <input type="hidden" name="status" value="Hired">
                                    <button type="submit" class="btn-success">✅ Confirm Hired</button>
                                </form>
                            {% elif app.student_response == 'Declined Offer' %}
                                <span style="color:#ef4444;font-size:13px;">Student declined the offer</span>
                            {% else %}
                                <span style="font-size:13px;color:#aaa;">⏳ Awaiting student decision...</span>
                            {% endif %}

                        {% elif app.status == 'Hired' %}
                            <a href="/employer/evaluate/{{ app.student.id }}/{{ app.internship.id }}/" class="btn-primary">⭐ Submit Evaluation</a>
                            <span style="font-size:13px;color:#15803d;font-weight:bold;">🎉 Hired!</span>

                        {% elif app.status == 'Rejected' or app.status == 'Withdrawn' %}
                            <span style="font-size:13px;color:#aaa;">Application {{ app.status|lower }}</span>
                        {% endif %}

                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color:#aaa;text-align:center;padding:30px;">No applications received yet.</p>
            {% endif %}
        </div>

        <!-- TAB 3: INTERN LOGS -->
        <div class="tab-panel" id="tab-logs">
            <h3 style="margin:16px 0 12px;">Weekly Logs from Interns</h3>
            {% if my_logs %}
                {% for log in my_logs %}
                <div class="card" style="border-left:4px solid #22c55e;">
                    <div style="display:flex;justify-content:space-between;">
                        <div>
                            <p style="font-weight:bold;margin:0 0 3px;">{{ log.student.get_full_name }} — Week {{ log.week_number }}</p>
                            <p style="font-size:13px;color:#555;">⏱ {{ log.hours_worked }} hours</p>
                            <p style="font-size:13px;color:#555;margin-top:4px;"><strong>Tasks:</strong> {{ log.tasks }}</p>
                            {% if log.challenges %}<p style="font-size:13px;color:#555;"><strong>Challenges:</strong> {{ log.challenges }}</p>{% endif %}
                            <p style="font-size:13px;color:#555;"><strong>Reflection:</strong> {{ log.reflection }}</p>
                        </div>
                        <p style="font-size:11px;color:#aaa;flex-shrink:0;">{{ log.submitted_at|date:"d M Y" }}</p>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color:#aaa;text-align:center;padding:30px;">No weekly logs submitted yet.</p>
            {% endif %}
        </div>

    </div>
</div>

<!-- INTERVIEW MODAL -->
<div class="modal-bg" id="interviewModal">
    <div class="modal-box">
        <h3 style="margin-bottom:16px;">📅 Schedule Interview</h3>
        <form method="POST" id="interviewForm">
            {% csrf_token %}
            <input type="hidden" name="status" value="Interview Scheduled">
            <div style="margin-bottom:14px;">
                <label style="font-weight:bold;font-size:14px;">Interview Date & Time *</label>
                <input type="text" name="interview_date" placeholder="e.g. 15 June 2026 at 10:00 AM via Zoom" style="margin-top:6px;">
            </div>
            <div style="margin-bottom:14px;">
                <label style="font-weight:bold;font-size:14px;">Additional Notes</label>
                <textarea name="interview_note" rows="3" placeholder="Location, format, what to prepare..." style="margin-top:6px;"></textarea>
            </div>
            <div style="display:flex;gap:10px;">
                <button type="submit" class="btn-primary" style="flex:1;padding:10px;">✅ Confirm Interview</button>
                <button type="button" onclick="closeModal()" style="flex:1;padding:10px;background:#f1f5f9;border:none;border-radius:6px;cursor:pointer;">Cancel</button>
            </div>
        </form>
    </div>
</div>

<form id="logout-form" method="POST" action="/logout/">{% csrf_token %}</form>
<footer><p>© 2026 IIPMS | Employer Dashboard</p></footer>

<script>
function showTab(name, btn) {
    document.querySelectorAll('.tab-panel').forEach(function(p){ p.classList.remove('active'); });
    document.querySelectorAll('.tab-btn').forEach(function(b){ b.classList.remove('active'); });
    document.getElementById('tab-' + name).classList.add('active');
    btn.classList.add('active');
}

function openInterviewModal(appId) {
    var form = document.getElementById('interviewForm');
    form.action = '/employer/application/' + appId + '/status/';
    document.getElementById('interviewModal').classList.add('show');
}

function closeModal() {
    document.getElementById('interviewModal').classList.remove('show');
}

document.getElementById('interviewModal').addEventListener('click', function(e){
    if (e.target === this) closeModal();
});
</script>
</body>
</html>"""

open(f, 'w').write(new_dashboard)
print("employer_dashboard.html completely rewritten")
