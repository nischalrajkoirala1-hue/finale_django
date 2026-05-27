with open('iipms_app/views.py', 'r') as f:
    content = f.read()

old = '''            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect_to_dashboard(user)'''

new = '''            login(request, user)
            return redirect_to_dashboard(user)'''

content = content.replace(old, new)

with open('iipms_app/views.py', 'w') as f:
    f.write(content)

print("done")
