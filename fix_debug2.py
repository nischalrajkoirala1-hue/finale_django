content = open('iipms_app/views.py').read()

old = "    if request.method == \"POST\":\n        first_name = request.POST.get(\"first_name\""

new = """    if request.method == "POST":
        print("DEBUG POST DATA:", dict(request.POST))
        first_name = request.POST.get("first_name\""""

content = content.replace(old, new)
open('iipms_app/views.py', 'w').write(content)
print("done")
