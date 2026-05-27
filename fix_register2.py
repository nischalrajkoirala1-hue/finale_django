content = open('iipms_app/views.py').read()

old = "        else:\n            # Build username from email"
new = "        else:\n            print('DEBUG: attempting to save user', email, role)\n            # Build username from email"

content = content.replace(old, new)

old2 = "            user.save()"
new2 = "            user.save()\n            print('DEBUG: user saved successfully', user.id)"

content = content.replace(old2, new2)

open('iipms_app/views.py', 'w').write(content)
print("done")
