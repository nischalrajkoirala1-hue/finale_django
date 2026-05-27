import re

f = 'iipms_app/templates/iipms_app/student_dashboard.html'
txt = open(f).read()

# Find and replace the TAB 1 internships section
# It currently has a search input and a div filled by JS showInternships()
# Replace with Django-rendered internship cards

old_tab1_search = '''            <input type="text" id="searchInput" placeholder="Search by title, company or skill..." onkeyup="showInternships()"'''

if old_tab1_search in txt:
    # Find the whole tab-1 panel
    start = txt.find('<!-- TAB 1:')
    # Find the next tab comment
    end = txt.find('<!-- TAB 2:', start)
    if end == -1:
        end = txt.find("<!-- TAB 3:", start)
    if end == -1:
        end = txt.find('id="tab-applications"', start)
    
    if start > -1 and end > -1:
        old_tab1 = txt[start:end]
        new_tab1 = """<!-- TAB 1: BROWSE INTERNSHIPS -->
        <div class="tab-panel active" id="tab-internships">
            <div style="margin:16px 0 12px;display:flex;justify-content:space-between;align-items:center;">
                <h3>Available Internships</h3>
                <a href="/student/internships/" style="font-size:13px;color:#4f6ef7;">View all →</a>
            </div>

            <!-- Search box -->
            <div style="margin-bottom:14px;">
                <input type="text" id="jobSearch" placeholder="Search by title, company or skill..."
                    style="width:100%;padding:11px 16px;border:1.5px solid #ddd;border-radius:8px;font-size:14px;box-sizing:border-box;"
                    onkeyup="filterJobs()">
            </div>

            <div id="jobCards">
            {% for item in internships_with_scores %}
            {% with job=item.job score=item.score bar=item.bar_colour applied=item.already_applied %}
            <div class="job-card card" style="margin-bottom:12px;border-left:4px solid #4f6ef7;"
                data-search="{{ job.title|lower }} {{ job.company|lower }} {{ job.skills|lower }} {{ job.location|lower }}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                    <div style="flex:1;">
                        <p style="font-weight:bold;font-size:15px;margin:0 0 4px;">{{ job.title }}</p>
                        <p style="font-size:13px;color:#555;margin:2px 0;">
                            🏢 {{ job.company }} &nbsp;|&nbsp; 📍 {{ job.location }}
                            {% if job.duration %}&nbsp;|&nbsp; ⏱ {{ job.duration }}{% endif %}
                            {% if job.stipend %}&nbsp;|&nbsp; 💰 {{ job.stipend }}{% endif %}
                        </p>
                        <!-- Skill pills -->
                        <div style="margin:6px 0;">
                            {% for skill in job.skills.split %}
                            <span style="background:#e8ecff;color:#4f6ef7;padding:2px 8px;border-radius:10px;font-size:11px;margin:2px;display:inline-block;">{{ skill }}</span>
                            {% endfor %}
                        </div>
                        {% if job.description %}
                        <p style="font-size:13px;color:#666;margin:4px 0;">{{ job.description }}</p>
                        {% endif %}
                        <!-- Match score bar -->
                        <p style="font-size:12px;color:#666;margin:4px 0;">
                            Skill match: <strong>{{ score }}%</strong>
                        </p>
                        <div style="background:#eee;border-radius:8px;height:8px;margin:4px 0;">
                            <div style="height:8px;border-radius:8px;width:{{ score }}%;background:{% if bar == 'green' %}#22c55e{% elif bar == 'orange' %}#f59e0b{% else %}#ef4444{% endif %};"></div>
                        </div>
                    </div>
                    <div style="flex-shrink:0;">
                        {% if applied %}
                        <span style="padding:7px 14px;background:#dcfce7;color:#15803d;border-radius:8px;font-size:13px;font-weight:bold;white-space:nowrap;">✓ Applied</span>
                        {% else %}
                        <form method="POST" action="/student/apply/{{ job.id }}/" style="margin:0;">
                            {% csrf_token %}
                            <button type="submit" style="padding:7px 16px;background:#4f6ef7;color:white;border:none;border-radius:8px;cursor:pointer;font-size:13px;white-space:nowrap;">Apply</button>
                        </form>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% endwith %}
            {% empty %}
            <p style="text-align:center;color:#aaa;padding:30px;">No internships available right now.</p>
            {% endfor %}
            </div>
        </div>

        """
        txt = txt[:start] + new_tab1 + txt[end:]
        print("Tab 1 internships replaced")
    else:
        print("Could not find tab boundaries, start:", start, "end:", end)
else:
    print("Search input not found")

open(f, 'w').write(txt)
print("student_dashboard.html saved")
