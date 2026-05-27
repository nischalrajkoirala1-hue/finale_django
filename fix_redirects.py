import glob, re, os

for f in glob.glob('iipms_app/templates/iipms_app/*.html'):
    txt = open(f).read()
    original = txt

    txt = re.sub(r'var user = getLoggedInUser\(\);\s*\n\s*if \(user === null\) \{[^}]*\}', '', txt)
    txt = re.sub(r'const user = getLoggedInUser\(\);\s*\n\s*if \(!user\) \{[^}]*\}', '', txt)
    txt = re.sub(r'if \(user === null\) \{\s*\n\s*window\.location\.href[^}]*\}', '', txt)
    txt = re.sub(r'if \(user === null\)\s*window\.location[^;]*;', '', txt)
    txt = re.sub(r'window\.location\.href\s*=\s*"login\.html"', '', txt)
    txt = re.sub(r'window\.location\.href\s*=\s*"\/login\/"', '', txt)
    txt = txt.replace('var user = getLoggedInUser();', '')
    txt = txt.replace('const user = getLoggedInUser();', '')
    txt = txt.replace("requireRole(\"student\")", 'null')
    txt = txt.replace("requireRole('student')", 'null')

    open(f, 'w').write(txt)
    if txt != original:
        print('fixed: ' + os.path.basename(f))

print('done')
