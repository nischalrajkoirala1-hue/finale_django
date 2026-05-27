# Fix the view to pass skills lists to the template
content = open('iipms_app/views.py').read()

old = '    return render(request, "iipms_app/post_internship.html", {"error": error})'

new = '''    skills_data = {
        "programming": ["Python","JavaScript","Java","C++","C#","TypeScript","Swift","Kotlin","Go","PHP","Ruby","R","MATLAB"],
        "web":         ["HTML","CSS","React","Vue.js","Angular","Node.js","Django","Flask","Next.js","Bootstrap","Tailwind CSS"],
        "data":        ["SQL","MySQL","PostgreSQL","MongoDB","Machine Learning","Deep Learning","TensorFlow","PyTorch","Pandas","NumPy","Tableau","Power BI","Excel"],
        "cloud":       ["AWS","Azure","Google Cloud","Docker","Kubernetes","Git","GitHub","CI/CD","Linux"],
        "other":       ["Figma","UI/UX Design","Agile","Scrum","REST APIs","GraphQL","Cybersecurity","Networking","React Native","Flutter"],
    }
    return render(request, "iipms_app/post_internship.html", {"error": error, "skills_data": skills_data})'''

if old in content:
    content = content.replace(old, new)
    open('iipms_app/views.py', 'w').write(content)
    print("view fixed")
else:
    print("NOT FOUND")
