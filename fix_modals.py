import os
import re

dir_path = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel'

csv_modal_html = """
    <!-- CSV Upload Modal -->
    <div id="csvUploadModal"
        class="hidden fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-opacity">
        <div class="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md transform scale-100 transition-transform">
            <h3 class="text-2xl font-bold text-slate-900 mb-6" id="csvModalTitle">Upload CSV</h3>
            <form id="csvUploadForm" onsubmit="uploadCSV(event)">
                <input type="hidden" id="csvModelType">
                <div class="space-y-5">
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Sub-Course</label>
                        <select id="csvCourseId" required
                            class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all outline-none appearance-none"></select>
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">CSV File</label>
                        <input type="file" id="csvFile" accept=".csv" required
                            class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 outline-none file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer">
                    </div>
                </div>
                <div class="flex justify-end gap-3 mt-8">
                    <button type="button" onclick="closeModal('csvUploadModal')"
                        class="px-5 py-2.5 rounded-xl font-semibold text-slate-600 hover:bg-slate-100 transition-all">Cancel</button>
                    <button type="submit" id="csvSubmitBtn"
                        class="bg-indigo-600 text-white px-6 py-2.5 rounded-xl font-semibold hover:bg-indigo-700 transition-all shadow-sm">Upload & Import</button>
                </div>
            </form>
        </div>
    </div>
"""

csv_modal_js = """
        function openCSVModal(modelType) {
            document.getElementById('csvModelType').value = modelType;
            document.getElementById('csvModalTitle').innerText = modelType === 'flashcard' ? 'Upload Flashcards CSV' : 'Upload MCQs CSV';
            document.getElementById('csvUploadModal').classList.remove('hidden');
        }

        async function uploadCSV(e) {
            e.preventDefault();
            const formData = new FormData();
            formData.append('model_type', document.getElementById('csvModelType').value);
            formData.append('subcourse_id', document.getElementById('csvCourseId').value);
            formData.append('file', document.getElementById('csvFile').files[0]);

            const btn = document.getElementById('csvSubmitBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = 'Uploading...';
            btn.disabled = true;

            try {
                const res = await apiCall('learning/admin/csv-upload/', 'POST', formData);
                if (res) {
                    showToast('Data imported successfully!');
                    closeModal('csvUploadModal');
                    setTimeout(() => location.reload(), 1000);
                }
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        }
"""

# Fix nav menu logic
old_nav_logic = """        // Set active nav button
        document.addEventListener('DOMContentLoaded', () => {
            const path = window.location.pathname;
            document.querySelectorAll('.nav-btn').forEach(btn => {
                if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(path.split('/')[2])) {
                    btn.className = "nav-btn w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all text-white bg-indigo-600 shadow-md shadow-indigo-900/20";
                }
            });
        });"""

new_nav_logic = """        // Set active nav button
        document.addEventListener('DOMContentLoaded', () => {
            const path = window.location.pathname;
            document.querySelectorAll('.nav-btn').forEach(btn => {
                const onclick = btn.getAttribute('onclick');
                if (onclick && onclick.includes(`'${path}'`)) {
                    btn.className = "nav-btn w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all text-white bg-indigo-600 shadow-md shadow-indigo-900/20";
                }
            });
        });"""


# 1. Base.html
base_path = os.path.join(dir_path, 'base.html')
with open(base_path, 'r', encoding='utf-8') as f:
    base = f.read()

base = base.replace(old_nav_logic, new_nav_logic + csv_modal_js)
base = base.replace('{% block content %}{% endblock %}', '{% block content %}{% endblock %}\n' + csv_modal_html)

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(base)


# 2. Replace loadAllData() in all specific htmls
for f_name in ['domains.html', 'courses.html', 'subcourses.html', 'flashcards.html', 'mcqs.html']:
    fp = os.path.join(dir_path, f_name)
    with open(fp, 'r', encoding='utf-8') as f:
        cont = f.read()
    
    # We want to replace loadAllData(); with location.reload();
    # Because dashboard.html still correctly uses loadAllData().
    cont = cont.replace("loadAllData();", "location.reload();")
    
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(cont)
