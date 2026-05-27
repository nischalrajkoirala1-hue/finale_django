import re
f = 'iipms_app/templates/iipms_app/post_internship.html'
txt = open(f).read()

# Replace all the broken .split loops with proper context variable loops
txt = re.sub(
    r'{% for s in ".*?\.split %}\s*\n\s*<span class="skill-tag" onclick="toggleSkill\(this\)">{{ s }}</span>\s*\n\s*{% endfor %}',
    '',
    txt
)

# Replace the entire skills picker section
old_section = '            <!-- REQUIRED SKILLS PICKER -->\n            <div style="margin-top:15px;">\n                <label><strong>Required Skills *</strong> — click to select</label>'

new_section = '''            <!-- REQUIRED SKILLS PICKER -->
            <div style="margin-top:15px;">
                <label><strong>Required Skills *</strong> — click to select</label>

                <div class="skills-category">Programming Languages</div>
                <div class="skills-grid">
                    {% for s in skills_data.programming %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>
                <div class="skills-category">Web Development</div>
                <div class="skills-grid">
                    {% for s in skills_data.web %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>
                <div class="skills-category">Data & AI</div>
                <div class="skills-grid">
                    {% for s in skills_data.data %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>
                <div class="skills-category">Cloud & DevOps</div>
                <div class="skills-grid">
                    {% for s in skills_data.cloud %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>
                <div class="skills-category">Other</div>
                <div class="skills-grid">
                    {% for s in skills_data.other %}
                    <span class="skill-tag" onclick="toggleSkill(this)">{{ s }}</span>
                    {% endfor %}
                </div>'''

if old_section in txt:
    txt = txt.replace(old_section, new_section)
    print("template section replaced cleanly")
else:
    # Rebuild the entire skills section from scratch
    print("doing full rebuild of skills section")
    txt = re.sub(
        r'<!-- REQUIRED SKILLS PICKER -->.*?<input type="text" id="customSkill"',
        new_section + '\n\n                <div style="margin-top:8px;">\n                    <input type="text" id="customSkill"',
        txt,
        flags=re.DOTALL
    )

open(f, 'w').write(txt)
print("template saved")
