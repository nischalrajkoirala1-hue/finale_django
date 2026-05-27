import os

TMPL = "iipms_app/templates/iipms_app"

# ── 1. POST INTERNSHIP TEMPLATE ──────────────────────────────
post_internship = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post Internship - IIPMS</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    <style>
        .form-container{max-width:700px;margin:30px auto;background:white;padding:30px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);}
        .success-box{background:#dcfce7;border:1.5px solid #22c55e;color:#15803d;padding:10px 14px;border-radius:8px;font-size:14px;margin-bottom:16px;}
        .error-box{background:#fee2e2;border:1.5px solid #ef4444;color:#b91c1c;padding:10px 14px;border-radius:8px;font-size:14px;margin-bottom:16px;}
        select,textarea,input{width:100%;padding:12px 14px;border:1px solid #cbd5e1;border-radius:6px;font-size:15px;outline:none;background:#fff;font-family:Arial,sans-serif;}
        textarea{resize:vertical;}
        .save-btn{width:100%;padding:12px;background:#4f6ef7;color:white;border:none;border-radius:6px;font-size:16px;cursor:pointer;margin-top:15px;}
        .skills-grid{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 12px;}
        .skill-tag{background:#e8ecff;color:#4f6ef7;padding:6px 12px;border-radius:20px;font-size:13px;cursor:pointer;border:1.5px solid transparent;user-select:none;}
        .skill-tag.selected{background:#4f6ef7;color:white;}
        .skill-tag:hover{border-color:#4f6ef7;}
        .skills-category{font-size:12px;font-weight:bold;color:#888;margin:10px 0 4px;text-transform:uppercase;}
    </style>
</head>
<body>
<header class="navbar">
    <div class="logo">IIPMS</div>
    <nav><ul>
        <li><a href="/employer/">Dashboard</a></li>
        <li><a href="/employer/post/" class="btn">Post Internship</a></li>
        <li><a href="/logout/">Logout</a></li>
    </ul></nav>
</header>

<div style="max-width:700px;margin:30px auto;padding:0 20px;">
    {% for message in messages %}
        <div class="success-box">{{ message }}</div>
    {% endfor %}
    {% if error %}
        <div class="error-box">{{ error }}</div>
    {% endif %}

    <div class="form-container">
        <h2 style="margin-bottom:20px;color:#1e293b;">📢 Post a New Internship</h2>

        <form method="POST">
            {% csrf_token %}

            <div class="input-group">
                <label><strong>Internship Title *</strong></label>
                <input type="text" name="title" required placeholder="e.g. Frontend Developer Intern">
            </div>

            <div class="input-row" style="display:flex;gap:15px;margin-top:15px;">
                <div class="input-group" style="flex:1;">
                    <label><strong>Location *</strong></label>
                    <input type="text" name="location" required placeholder="e.g. Sydney / Remote">
                </div>
                <div class="input-group" style="flex:1;">
                    <label><strong>Duration</strong></label>
                    <input type="text" name="duration" placeholder="e.g. 3 months">
                </div>
            </div>

            <div class="input-row" style="display:flex;gap:15px;margin-top:15px;">
                <div class="input-group" style="flex:1;">
                    <label><strong>Start Date</strong></label>
                    <input type="text" name="start_date" placeholder="e.g. 1 July 2026">
                </div>
                <div class="input-group" style="flex:1;">
                    <label><strong>End Date</strong></label>
                    <input type="text" name="end_date" placeholder="e.g. 30 September 2026">
                </div>
            </div>

            <div class="input-row" style="display:flex;gap:15px;margin-top:15px;">
                <div class="input-group" style="flex:1;">
                    <label><strong>Stipend / Pay</strong></label>
                    <input type="text" name="stipend" placeholder="e.g. $600/week or Unpaid">
                </div>
                <div class="input-group" style="flex:1;">
                    <label><strong>Work Type</strong></label>
                    <select name="work_type">
                        <option value="">Select...</option>
                        <option value="On-site">On-site</option>
                        <option value="Remote">Remote</option>
                        <option value="Hybrid">Hybrid</option>
                    </select>
                </div>
            </div>

            <div style="margin-top:15px;">
                <label><strong>Industry</strong></label>
                <select name="industry" style="margin-top:6px;">
                    <option value="">Select industry...</option>
                    <option value="Technology">Technology / IT</option>
                    <option value="Finance">Finance / Banking</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Engineering">Engineering</option>
                    <option value="Marketing">Marketing</option>
                    <option value="Education">Education</option>
                    <option value="Other">Other</option>
                </select>
            </div>

            <div style="margin-top:15px;">
                <label><strong>Description</strong></label>
                <textarea name="description" rows="3" style="margin-top:6px;" placeholder="Describe the role, responsibilities, and what the intern will learn..."></textarea>
            </div>

            <!-- REQUIRED SKILLS PICKER -->
            <div style="margin-top:15px;">
                <label><strong>Required Skills *</strong> — click to select</label>

                <div class="skills-category">Programming Languages</div>
                <div class="skills-grid">
                    {% for s in "Python,JavaScript,Java,C++,C#,TypeScript,Swift,Kotlin,Go,PHP,Ruby,R".split %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>
                <div class="skills-category">Web Development</div>
                <div class="skills-grid">
                    {% for s in "HTML,CSS,React,Vue.js,Angular,Node.js,Django,Flask,Next.js,Bootstrap,Tailwind CSS".split %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>
                <div class="skills-category">Data & AI</div>
                <div class="skills-grid">
                    {% for s in "SQL,MySQL,PostgreSQL,MongoDB,Machine Learning,TensorFlow,Pandas,NumPy,Tableau,Power BI,Excel".split %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>
                <div class="skills-category">Cloud & DevOps</div>
                <div class="skills-grid">
                    {% for s in "AWS,Azure,Google Cloud,Docker,Kubernetes,Git,GitHub,Linux".split %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>
                <div class="skills-category">Other</div>
                <div class="skills-grid">
                    {% for s in "Figma,UI/UX Design,Agile,Scrum,REST APIs,Cybersecurity,Networking".split %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>

                <div style="margin-top:8px;">
                    <input type="text" id="customSkill" placeholder="Type a custom skill and press Enter" onkeydown="addCustom(event)" style="margin-top:0;">
                </div>
                <input type="hidden" name="skills" id="skillsInput">
                <p style="font-size:13px;color:#4f6ef7;margin-top:6px;" id="skillCount">0 skills selected</p>
            </div>

            <button type="submit" class="save-btn">📢 Post Internship</button>
            <p style="text-align:center;margin-top:12px;"><a href="/employer/" style="color:#4f6ef7;">← Back to Dashboard</a></p>
        </form>
    </div>
</div>

<footer><p>© 2026 IIPMS</p></footer>

<script>
var selected = [];
function toggleSkill(el) {
    var s = el.textContent.trim();
    var i = selected.indexOf(s);
    if (i === -1) { selected.push(s); el.classList.add('selected'); }
    else { selected.splice(i,1); el.classList.remove('selected'); }
    update();
}
function addCustom(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        var v = document.getElementById('customSkill').value.trim();
        if (v && selected.indexOf(v) === -1) { selected.push(v); update(); document.getElementById('customSkill').value=''; }
    }
}
function update() {
    document.getElementById('skillsInput').value = selected.join(', ');
    document.getElementById('skillCount').textContent = selected.length + ' skill(s) selected: ' + selected.join(', ');
}
</script>
</body>
</html>"""

open(os.path.join(TMPL, "post_internship.html"), "w").write(post_internship)
print("post_internship.html done")

# ── 2. ISSUE OFFER TEMPLATE ──────────────────────────────────
issue_offer = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Issue Offer - IIPMS</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    <style>
        .form-container{max-width:600px;margin:30px auto;background:white;padding:30px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);}
        input,textarea,select{width:100%;padding:12px 14px;border:1px solid #cbd5e1;border-radius:6px;font-size:15px;outline:none;font-family:Arial,sans-serif;}
        textarea{resize:vertical;}
        .save-btn{width:100%;padding:12px;background:#22c55e;color:white;border:none;border-radius:6px;font-size:16px;cursor:pointer;margin-top:15px;}
    </style>
</head>
<body>
<header class="navbar">
    <div class="logo">IIPMS</div>
    <nav><ul>
        <li><a href="/employer/">Dashboard</a></li>
        <li><a href="/logout/">Logout</a></li>
    </ul></nav>
</header>

<div style="max-width:600px;margin:30px auto;padding:0 20px;">
    <div class="form-container">
        <h2 style="margin-bottom:6px;">📄 Issue Offer Letter</h2>
        <p style="color:#555;font-size:14px;margin-bottom:20px;">
            Sending offer to: <strong>{{ app.student.get_full_name }}</strong><br>
            For: <strong>{{ app.internship.title }}</strong>
        </p>

        <form method="POST">
            {% csrf_token %}
            <div class="input-group" style="margin-bottom:15px;">
                <label><strong>Start Date *</strong></label>
                <input type="text" name="start_date" required placeholder="e.g. 1 July 2026" style="margin-top:6px;">
            </div>
            <div class="input-group" style="margin-bottom:15px;">
                <label><strong>End Date *</strong></label>
                <input type="text" name="end_date" required placeholder="e.g. 30 September 2026" style="margin-top:6px;">
            </div>
            <div class="input-group" style="margin-bottom:15px;">
                <label><strong>Stipend / Pay</strong></label>
                <input type="text" name="stipend" placeholder="e.g. $600/week or Unpaid" style="margin-top:6px;">
            </div>
            <div class="input-group" style="margin-bottom:15px;">
                <label><strong>Terms & Conditions</strong></label>
                <textarea name="terms" rows="4" placeholder="Any specific terms, conditions or requirements..." style="margin-top:6px;"></textarea>
            </div>
            <button type="submit" class="save-btn">✅ Send Offer for Approval</button>
            <p style="text-align:center;margin-top:12px;"><a href="/employer/" style="color:#4f6ef7;">← Cancel</a></p>
        </form>
    </div>
</div>
<footer><p>© 2026 IIPMS</p></footer>
</body>
</html>"""

open(os.path.join(TMPL, "issue_offer.html"), "w").write(issue_offer)
print("issue_offer.html done")

# ── 3. SUBMIT EVALUATION TEMPLATE ────────────────────────────
evaluation = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Submit Evaluation - IIPMS</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    <style>
        .form-container{max-width:600px;margin:30px auto;background:white;padding:30px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);}
        input,textarea,select{width:100%;padding:12px 14px;border:1px solid #cbd5e1;border-radius:6px;font-size:15px;outline:none;font-family:Arial,sans-serif;}
        textarea{resize:vertical;}
        .save-btn{width:100%;padding:12px;background:#4f6ef7;color:white;border:none;border-radius:6px;font-size:16px;cursor:pointer;margin-top:15px;}
        .rating-row{display:flex;gap:10px;margin:6px 0 15px;}
        .rating-row label{flex:1;text-align:center;padding:10px;border:1.5px solid #cbd5e1;border-radius:8px;cursor:pointer;font-size:14px;}
        .rating-row input[type=radio]{display:none;}
        .rating-row input[type=radio]:checked + label{background:#4f6ef7;color:white;border-color:#4f6ef7;}
    </style>
</head>
<body>
<header class="navbar">
    <div class="logo">IIPMS</div>
    <nav><ul>
        <li><a href="/employer/">Dashboard</a></li>
        <li><a href="/logout/">Logout</a></li>
    </ul></nav>
</header>

<div style="max-width:600px;margin:30px auto;padding:0 20px;">
    <div class="form-container">
        <h2 style="margin-bottom:6px;">⭐ Submit Evaluation</h2>
        <p style="color:#555;font-size:14px;margin-bottom:20px;">
            Evaluating: <strong>{{ student.get_full_name }}</strong><br>
            Internship: <strong>{{ internship.title }}</strong>
        </p>

        <form method="POST">
            {% csrf_token %}

            {% for field_name, field_label in ratings %}
            <div style="margin-bottom:15px;">
                <label><strong>{{ field_label }}</strong></label>
                <div class="rating-row">
                    {% for i in "12345" %}
                    <input type="radio" name="{{ field_name }}" id="{{ field_name }}_{{ i }}" value="{{ i }}" required>
                    <label for="{{ field_name }}_{{ i }}">{{ i }}{% if i == "1" %} ⭐{% elif i == "5" %} 🌟{% endif %}</label>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}

            <div style="margin-bottom:15px;">
                <label><strong>Comments</strong></label>
                <textarea name="comments" rows="4" placeholder="Describe the intern's performance..." style="margin-top:6px;"></textarea>
            </div>

            <div style="margin-bottom:15px;">
                <label><strong>Recommendation</strong></label>
                <select name="recommendation" style="margin-top:6px;">
                    <option value="">Select...</option>
                    <option value="Highly Recommend">Highly Recommend</option>
                    <option value="Recommend">Recommend</option>
                    <option value="Neutral">Neutral</option>
                    <option value="Needs Improvement">Needs Improvement</option>
                    <option value="Would Not Rehire">Would Not Rehire</option>
                </select>
            </div>

            <button type="submit" class="save-btn">📤 Submit Evaluation</button>
            <p style="text-align:center;margin-top:12px;"><a href="/employer/" style="color:#4f6ef7;">← Cancel</a></p>
        </form>
    </div>
</div>
<footer><p>© 2026 IIPMS</p></footer>
</body>
</html>"""

open(os.path.join(TMPL, "submit_evaluation.html"), "w").write(evaluation)
print("submit_evaluation.html done")

print("\nAll templates created!")
