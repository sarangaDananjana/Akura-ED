import os

dir_path = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel'

# 1. Update courses.html
c_path = os.path.join(dir_path, 'courses.html')
with open(c_path, 'r', encoding='utf-8') as f:
    cont = f.read()

# Add price input
price_html = """                      <div>
                          <label class="block text-sm font-semibold text-slate-700 mb-2">Price ($)</label>
                          <input type="number" step="0.01" id="parentCoursePrice" required
                              class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all outline-none">
                      </div>"""
if "parentCoursePrice" not in cont:
    cont = cont.replace(
        """                      <div>
                          <label class="block text-sm font-semibold text-slate-700 mb-2">Description</label>""",
        price_html + """\n                      <div>
                          <label class="block text-sm font-semibold text-slate-700 mb-2">Description</label>"""
    )

# Update submitParentCourse
cont = cont.replace(
    "description: document.getElementById('parentCourseDesc').value,",
    "description: document.getElementById('parentCourseDesc').value,\n                price: document.getElementById('parentCoursePrice').value,"
)

# Update editParentCourse
cont = cont.replace(
    "document.getElementById('parentCourseDesc').value = c.description;",
    "document.getElementById('parentCourseDesc').value = c.description;\n            document.getElementById('parentCoursePrice').value = c.price || '0.00';"
)

with open(c_path, 'w', encoding='utf-8') as f:
    f.write(cont)


# 2. Update subcourses.html
s_path = os.path.join(dir_path, 'subcourses.html')
with open(s_path, 'r', encoding='utf-8') as f:
    cont = f.read()

# Add is_free toggle
free_html = """                      <label
                          class="flex items-center gap-3 p-4 border border-emerald-100 bg-emerald-50/50 rounded-xl cursor-pointer hover:bg-emerald-50 transition-colors">
                          <input type="checkbox" id="courseIsFree"
                              class="w-5 h-5 text-emerald-600 rounded focus:ring-emerald-500 border-gray-300">
                          <div>
                              <span class="block text-sm font-bold text-emerald-900">Is Free</span>
                              <span class="block text-xs text-emerald-700 mt-0.5">Users can access this without buying the main course</span>
                          </div>
                      </label>"""
if "courseIsFree" not in cont:
    cont = cont.replace(
        """                      <label
                          class="flex items-center gap-3 p-4 border border-slate-100 rounded-xl cursor-pointer""",
        free_html + """\n                      <label
                          class="flex items-center gap-3 p-4 border border-slate-100 rounded-xl cursor-pointer"""
    )

# Update submitCourse
cont = cont.replace(
    "description: document.getElementById('courseDesc').value,",
    "description: document.getElementById('courseDesc').value,\n                is_free: document.getElementById('courseIsFree').checked,"
)

# Update editCourse
cont = cont.replace(
    "document.getElementById('courseDesc').value = c.description;",
    "document.getElementById('courseDesc').value = c.description;\n            document.getElementById('courseIsFree').checked = c.is_free;"
)

with open(s_path, 'w', encoding='utf-8') as f:
    f.write(cont)
