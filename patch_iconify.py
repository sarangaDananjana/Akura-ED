import re
import os

BASE_DIR = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel'

# 1. Update base.html
base_path = os.path.join(BASE_DIR, 'base.html')
with open(base_path, 'r', encoding='utf-8') as f:
    base_html = f.read()

iconify_script = '<script src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"></script>'
if iconify_script not in base_html:
    base_html = base_html.replace('</head>', f'    {iconify_script}\n</head>')

icon_picker_modal = """
    <!-- Icon Picker Modal -->
    <div id="iconPickerModal" class="hidden fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-[60] p-4 transition-opacity">
        <div class="bg-white rounded-3xl shadow-2xl p-6 w-full max-w-2xl transform scale-100 transition-transform flex flex-col max-h-[80vh]">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-2xl font-bold text-slate-900">Choose Icon</h3>
                <button onclick="closeModal('iconPickerModal')" class="text-slate-400 hover:text-slate-600"><i class="ph ph-x text-2xl"></i></button>
            </div>
            
            <div class="relative mb-6">
                <i class="ph ph-magnifying-glass absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 text-lg"></i>
                <input type="text" id="iconSearchInput" placeholder="Search icons (e.g., book, math, science)..." 
                    class="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-700 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all">
            </div>

            <div id="iconGrid" class="flex-1 overflow-y-auto grid grid-cols-6 sm:grid-cols-8 gap-4 p-2">
                <!-- Icons injected here -->
            </div>
            
            <div class="mt-4 flex justify-end">
                <button onclick="closeModal('iconPickerModal')" class="px-5 py-2.5 rounded-xl font-semibold text-slate-600 hover:bg-slate-100 transition-all">Cancel</button>
            </div>
        </div>
    </div>
"""

if "iconPickerModal" not in base_html:
    base_html = base_html.replace('<!-- CSV Upload Modal -->', icon_picker_modal + '\n    <!-- CSV Upload Modal -->')

icon_picker_script = """
        let currentIconTarget = null;
        let searchTimeout = null;

        function openIconPicker(targetInputId) {
            currentIconTarget = targetInputId;
            document.getElementById('iconPickerModal').classList.remove('hidden');
            const input = document.getElementById('iconSearchInput');
            input.value = '';
            document.getElementById('iconGrid').innerHTML = '<p class="col-span-full text-center text-slate-500 py-8">Type to search for icons...</p>';
            input.focus();
        }

        document.getElementById('iconSearchInput')?.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            if (query.length < 2) return;
            
            searchTimeout = setTimeout(async () => {
                const grid = document.getElementById('iconGrid');
                grid.innerHTML = '<div class="col-span-full flex justify-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div></div>';
                
                try {
                    const res = await fetch(`https://api.iconify.design/search?query=${encodeURIComponent(query)}&limit=64`);
                    const data = await res.json();
                    
                    if (data.icons && data.icons.length > 0) {
                        grid.innerHTML = data.icons.map(icon => `
                            <button onclick="selectIcon('${icon}')" class="flex flex-col items-center justify-center p-3 rounded-xl hover:bg-indigo-50 hover:text-indigo-600 transition-colors border border-transparent hover:border-indigo-100 group">
                                <iconify-icon icon="${icon}" class="text-3xl text-slate-600 group-hover:text-indigo-600 transition-colors"></iconify-icon>
                            </button>
                        `).join('');
                    } else {
                        grid.innerHTML = '<p class="col-span-full text-center text-slate-500 py-8">No icons found.</p>';
                    }
                } catch (err) {
                    grid.innerHTML = '<p class="col-span-full text-center text-red-500 py-8">Failed to load icons.</p>';
                }
            }, 500);
        });

        function selectIcon(iconId) {
            if (currentIconTarget) {
                const targetInput = document.getElementById(currentIconTarget);
                if (targetInput) targetInput.value = iconId;
                
                // Update preview if it exists
                const preview = document.getElementById(currentIconTarget + 'Preview');
                if (preview) {
                    preview.innerHTML = `<iconify-icon icon="${iconId}" class="text-2xl text-indigo-600"></iconify-icon>`;
                }
            }
            closeModal('iconPickerModal');
        }
"""

if "openIconPicker" not in base_html:
    base_html = base_html.replace('function openCSVModal(modelType) {', icon_picker_script + '\n        function openCSVModal(modelType) {')

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(base_html)


# 2. Update courses.html
courses_path = os.path.join(BASE_DIR, 'courses.html')
with open(courses_path, 'r', encoding='utf-8') as f:
    courses_html = f.read()

course_icon_input = """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Icon</label>
                        <div class="flex items-center gap-3">
                            <div id="parentCourseIconPreview" class="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center">
                                <i class="ph ph-image text-slate-400"></i>
                            </div>
                            <input type="hidden" id="parentCourseIcon" value="">
                            <button type="button" onclick="openIconPicker('parentCourseIcon')" class="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm">
                                Choose Icon
                            </button>
                        </div>
                    </div>"""

if "parentCourseIcon" not in courses_html:
    courses_html = courses_html.replace(
        """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Course Title</label>""",
        course_icon_input + """\n                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Course Title</label>"""
    )

# update table rows for parent courses to show icon
if "<iconify-icon icon=\"${c.icon}\"" not in courses_html:
    courses_html = courses_html.replace(
        '<td class="px-6 py-4 font-bold text-slate-800">${c.title}</td>',
        '<td class="px-6 py-4 font-bold text-slate-800 flex items-center gap-3">${c.icon ? `<iconify-icon icon="${c.icon}" class="text-xl text-indigo-600"></iconify-icon>` : `<i class="ph ph-book text-xl text-slate-400"></i>`} ${c.title}</td>'
    )

courses_html = courses_html.replace(
    "price: document.getElementById('parentCoursePrice').value, is_active: document.getElementById('parentCourseActive').checked };",
    "price: document.getElementById('parentCoursePrice').value, icon: document.getElementById('parentCourseIcon').value, is_active: document.getElementById('parentCourseActive').checked };"
)

if "document.getElementById('parentCourseIcon').value = c.icon || '';" not in courses_html:
    courses_html = courses_html.replace(
        "document.getElementById('parentCoursePrice').value = c.price || '0.00';",
        "document.getElementById('parentCoursePrice').value = c.price || '0.00';\n            document.getElementById('parentCourseIcon').value = c.icon || '';\n            document.getElementById('parentCourseIconPreview').innerHTML = c.icon ? `<iconify-icon icon=\"${c.icon}\" class=\"text-2xl text-indigo-600\"></iconify-icon>` : `<i class=\"ph ph-image text-slate-400\"></i>`;"
    )
    
    courses_html = courses_html.replace(
        "document.getElementById('parentCourseModalTitle').innerText = isEdit ? 'Edit Parent Course' : 'Add Parent Course';",
        "document.getElementById('parentCourseModalTitle').innerText = isEdit ? 'Edit Parent Course' : 'Add Parent Course';\n                if(!isEdit) { document.getElementById('parentCourseIcon').value = ''; document.getElementById('parentCourseIconPreview').innerHTML = `<i class=\"ph ph-image text-slate-400\"></i>`; }"
    )

with open(courses_path, 'w', encoding='utf-8') as f:
    f.write(courses_html)


# 3. Update subcourses.html
subcourses_path = os.path.join(BASE_DIR, 'subcourses.html')
with open(subcourses_path, 'r', encoding='utf-8') as f:
    subcourses_html = f.read()

subcourse_icon_input = """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Icon</label>
                        <div class="flex items-center gap-3">
                            <div id="courseIconPreview" class="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center">
                                <i class="ph ph-image text-slate-400"></i>
                            </div>
                            <input type="hidden" id="courseIcon" value="">
                            <button type="button" onclick="openIconPicker('courseIcon')" class="px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm">
                                Choose Icon
                            </button>
                        </div>
                    </div>"""

if "courseIcon" not in subcourses_html:
    subcourses_html = subcourses_html.replace(
        """                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Sub-Course Title</label>""",
        subcourse_icon_input + """\n                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Sub-Course Title</label>"""
    )

if "<iconify-icon icon=\"${c.icon}\"" not in subcourses_html:
    subcourses_html = subcourses_html.replace(
        '<td class="px-6 py-4 font-bold text-slate-800">${c.title}</td>',
        '<td class="px-6 py-4 font-bold text-slate-800 flex items-center gap-3">${c.icon ? `<iconify-icon icon="${c.icon}" class="text-xl text-indigo-600"></iconify-icon>` : `<i class="ph ph-book-open text-xl text-slate-400"></i>`} ${c.title}</td>'
    )

subcourses_html = subcourses_html.replace(
    "is_free: document.getElementById('courseIsFree').checked, is_active: document.getElementById('courseActive').checked };",
    "is_free: document.getElementById('courseIsFree').checked, icon: document.getElementById('courseIcon').value, is_active: document.getElementById('courseActive').checked };"
)

if "document.getElementById('courseIcon').value = c.icon || '';" not in subcourses_html:
    subcourses_html = subcourses_html.replace(
        "document.getElementById('courseIsFree').checked = c.is_free;",
        "document.getElementById('courseIsFree').checked = c.is_free;\n            document.getElementById('courseIcon').value = c.icon || '';\n            document.getElementById('courseIconPreview').innerHTML = c.icon ? `<iconify-icon icon=\"${c.icon}\" class=\"text-2xl text-indigo-600\"></iconify-icon>` : `<i class=\"ph ph-image text-slate-400\"></i>`;"
    )
    
    subcourses_html = subcourses_html.replace(
        "document.getElementById('courseModalTitle').innerText = isEdit ? 'Edit Sub-Course' : 'Add Sub-Course';",
        "document.getElementById('courseModalTitle').innerText = isEdit ? 'Edit Sub-Course' : 'Add Sub-Course';\n                if(!isEdit) { document.getElementById('courseIcon').value = ''; document.getElementById('courseIconPreview').innerHTML = `<i class=\"ph ph-image text-slate-400\"></i>`; }"
    )

with open(subcourses_path, 'w', encoding='utf-8') as f:
    f.write(subcourses_html)

print("Iconify patch applied successfully.")
