import os
import re

directory = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel'

fixes = {
    'domains.html': "document.getElementById('stat-domains').innerText = state.domains.length;",
    'courses.html': "document.getElementById('stat-parentcourses').innerText = state.parentcourses.length;",
    'subcourses.html': "document.getElementById('stat-courses').innerText = state.courses.length;",
    'flashcards.html': "document.getElementById('stat-flashcards').innerText = state.flashcards.length;",
    'mcqs.html': "document.getElementById('stat-mcqs').innerText = state.mcqs.length;"
}

# Also need to check if state.domains.find is crashing if domains weren't loaded in subcourses.html!
# In subcourses.html, it uses state.domains.find(d => d.id === c.domain)?.title
# But subcourses.html only fetches `parentcourses` on load! It DOES NOT fetch `domains`.
# Wait, look at `subcourses.html` script:
# `const pData = await apiCall('learning/admin/courses/'); if(pData) { state.parentcourses = pData.results || pData; populateParentCourseDropdowns(); fetchFilteredCourses(); }`
# And `renderCourses` uses `state.domains.find`!
# So state.domains is empty! It won't crash because of `?.title || 'Unknown'`, it will just display 'Unknown'.
# BUT it would be better if we fetch domains as well so it shows correctly!

for filename, stat_str in fixes.items():
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the stat string and any optional whitespace/semicolons around it
        # Actually it's simpler to just do a string replace since I generated them exactly this way.
        # Wait, the stat_str might be `document.getElementById('stat-domains').innerText = state.domains.length;`
        # Let's use regex to be safe
        pattern = re.compile(r"document\.getElementById\('stat-\w+'\)(?:\?)?\.innerText\s*=\s*[^;]+;")
        content = pattern.sub('', content)

        # Fix subcourses.html missing domains
        if filename == 'subcourses.html':
            missing_fetch = "const dData = await apiCall('learning/admin/domains/'); if(dData) { state.domains = dData.results || dData; }"
            if "state.domains = dData.results" not in content:
                content = content.replace("const pData = await apiCall('learning/admin/courses/');", f"{missing_fetch}\nconst pData = await apiCall('learning/admin/courses/');")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Stat updates removed from individual pages, and subcourses.html missing dependencies fixed.")
