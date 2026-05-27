import os, glob, re

tmpl_dir = "iipms_app/templates/iipms_app"

for fpath in glob.glob(tmpl_dir + "/*.html"):
    with open(fpath, "r") as f:
        content = f.read()

    content = re.sub(r"onclick=\"window\.location\.href='[^']*logout[^']*'\"", "onclick=\"document.getElementById('logout-form').submit();\"", content)

    if 'id="logout-form"' not in content:
        form = '<form id="logout-form" method="POST" action="{% url ' + "'logout'" + ' %}">{% csrf_token %}</form>'
        content = content.replace("</body>", form + "\n</body>")

    with open(fpath, "w") as f:
        f.write(content)
    print("fixed: " + os.path.basename(fpath))

print("All done!")
